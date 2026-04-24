import json
import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.pipeline import LineageEdge, PipelineExpectationResult, PipelineRun
from app.schemas.pipeline import PipelineExpectation


def serialize_expectations(expectations: list[PipelineExpectation]) -> str:
    return json.dumps([item.model_dump() for item in expectations])


def deserialize_expectations(expectations_json: str | None) -> list[dict[str, Any]]:
    if not expectations_json:
        return []
    return json.loads(expectations_json)


def _extract_row_count_preview(output_json: str | None) -> int | None:
    if not output_json:
        return None
    try:
        payload = json.loads(output_json)
    except json.JSONDecodeError:
        return None
    value = payload.get("row_count_preview")
    return value if isinstance(value, int) else None


def evaluate_expectations(
    db: Session, pipeline_run: PipelineRun, expectations_json: str | None, output_json: str | None
) -> list[PipelineExpectationResult]:
    expectations = deserialize_expectations(expectations_json)
    row_count_preview = _extract_row_count_preview(output_json)
    results: list[PipelineExpectationResult] = []

    for expectation in expectations:
      status = "UNKNOWN"
      detail = "Constraint parser did not recognize the rule."
      rule = expectation["constraint_sql"].strip()

      gt_match = re.fullmatch(r"row_count_preview\s*>\s*(\d+)", rule, re.IGNORECASE)
      ge_match = re.fullmatch(r"row_count_preview\s*>=\s*(\d+)", rule, re.IGNORECASE)
      type_match = re.fullmatch(r"output_type\s*=\s*'([^']+)'", rule, re.IGNORECASE)

      if gt_match and row_count_preview is not None:
          minimum = int(gt_match.group(1))
          passed = row_count_preview > minimum
          status = "PASS" if passed else "FAIL"
          detail = f"row_count_preview={row_count_preview}"
      elif ge_match and row_count_preview is not None:
          minimum = int(ge_match.group(1))
          passed = row_count_preview >= minimum
          status = "PASS" if passed else "FAIL"
          detail = f"row_count_preview={row_count_preview}"
      elif type_match and output_json:
          payload = json.loads(output_json)
          expected_type = type_match.group(1)
          actual_type = payload.get("type")
          passed = actual_type == expected_type
          status = "PASS" if passed else "FAIL"
          detail = f"output_type={actual_type}"

      result = PipelineExpectationResult(
          pipeline_run_id=pipeline_run.id,
          expectation_name=expectation["name"],
          constraint_sql=expectation["constraint_sql"],
          action=expectation.get("action", "WARN").upper(),
          status=status,
          detail=detail,
      )
      db.add(result)
      results.append(result)

    db.commit()
    for result in results:
      db.refresh(result)
    return results


def create_lineage_edges(
    db: Session,
    pipeline_run_id: int,
    notebook_path: str,
    pipeline_name: str,
    target_fqn: str,
) -> list[LineageEdge]:
    edges = [
        LineageEdge(
            pipeline_run_id=pipeline_run_id,
            source_type="NOTEBOOK",
            source_name=notebook_path,
            target_type="TABLE",
            target_name=target_fqn,
            relation_type="WRITES",
        ),
        LineageEdge(
            pipeline_run_id=pipeline_run_id,
            source_type="PIPELINE",
            source_name=pipeline_name,
            target_type="TABLE",
            target_name=target_fqn,
            relation_type="DERIVES",
        ),
    ]
    db.add_all(edges)
    db.commit()
    for edge in edges:
        db.refresh(edge)
    return edges


def get_pipeline_expectation_results(db: Session, pipeline_run_id: int) -> list[PipelineExpectationResult]:
    stmt = (
        select(PipelineExpectationResult)
        .where(PipelineExpectationResult.pipeline_run_id == pipeline_run_id)
        .order_by(PipelineExpectationResult.id)
    )
    return list(db.scalars(stmt).all())


def get_lineage_edges(db: Session, pipeline_run_id: int | None = None) -> list[LineageEdge]:
    stmt = select(LineageEdge).order_by(LineageEdge.created_at.desc(), LineageEdge.id.desc())
    if pipeline_run_id is not None:
        stmt = stmt.where(LineageEdge.pipeline_run_id == pipeline_run_id)
    return list(db.scalars(stmt).all())
