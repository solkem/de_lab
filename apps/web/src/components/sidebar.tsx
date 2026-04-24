type SidebarProps = {
  activeItem?: string;
};

const sections = [
  {
    label: "Build",
    items: ["Workspace", "Notebooks", "SQL Editor", "Projects"],
  },
  {
    label: "Operate",
    items: ["Catalog", "Jobs", "Pipelines", "Compute"],
  },
  {
    label: "Observe",
    items: ["Lineage", "System Tables"],
  },
];


export function Sidebar({ activeItem = "Workspace" }: SidebarProps) {
  return (
    <aside className="sidebar">
      {sections.map((section) => (
        <div className="nav-group" key={section.label}>
          <p className="nav-label">{section.label}</p>
          {section.items.map((item, index) => {
            const isActive =
              item === activeItem ||
              (section.label === "Build" && index === 0 && activeItem === "Workspace");

            return (
              <a
                className={`nav-item ${isActive ? "active" : ""}`}
                href={
                  item === "Notebooks"
                    ? "/notebooks"
                    : item === "Jobs"
                      ? "/jobs"
                      : item === "Pipelines"
                        ? "/pipelines"
                        : item === "Lineage"
                          ? "/lineage"
                        : "#"
                }
                key={item}
              >
                {item}
              </a>
            );
          })}
        </div>
      ))}
    </aside>
  );
}
