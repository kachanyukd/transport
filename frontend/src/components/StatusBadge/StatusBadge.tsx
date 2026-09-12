import styles from "./StatusBadge.module.css";

type Status = string;

const STATUS_COLORS: Record<string, string> = {
  active: "green",
  maintenance: "orange",
  decommissioned: "red",
  dismissed: "gray",
  open: "blue",
  closed: "green",
  planned_to: "blue",
  current_repair: "orange",
  major_repair: "red",
};

interface Props {
  status: Status;
  label?: string;
}

export default function StatusBadge({ status, label }: Props) {
  const color = STATUS_COLORS[status] ?? "gray";
  return (
    <span className={`${styles.badge} ${styles[color]}`}>
      {label ?? status.replace(/_/g, " ")}
    </span>
  );
}
