import styles from "./MockFillButton.module.css";

interface Props {
  onClick: () => void;
  loading?: boolean;
}

export default function MockFillButton({ onClick, loading }: Props) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={loading}
      className={styles.btn}
      title="Fill form with demo data"
    >
      ⚡ Demo
    </button>
  );
}
