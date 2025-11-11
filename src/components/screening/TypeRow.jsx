import '../../styles/app.css';

export default function TypeRow({
  title,
  description,
  name,
  value,
  onChange
}) {
  return (
    <li className="type-row">
      <div className="type-main">
        <div className="type-title">{title}</div>
        <div className="type-sub">{description}</div>
      </div>
      <div className="type-opts">
        <label className="opt">
          <input
            type="radio"
            name={name}
            value="yes"
            checked={value === 'yes'}
            onChange={onChange}
            data-audit-label={`${title} — yes`}
          />
          <span>Yes</span>
        </label>
        <label className="opt">
          <input
            type="radio"
            name={name}
            value="sometimes"
            checked={value === 'sometimes'}
            onChange={onChange}
            data-audit-label={`${title} — sometimes`}
          />
          <span>Sometimes</span>
        </label>
        <label className="opt">
          <input
            type="radio"
            name={name}
            value="no"
            checked={value === 'no'}
            onChange={onChange}
            data-audit-label={`${title} — no`}
          />
          <span>No</span>
        </label>
      </div>
    </li>
  );
}
