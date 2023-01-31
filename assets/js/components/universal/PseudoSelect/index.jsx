import React from 'react';

export default function PseudoSelect(props) {
  const {
    open,
    items,
    loading,
    changeAction,
    name,
    selected
  } = props;

  const keys = Object.keys(items);
  const radioChange = event => changeAction(event.target.value);

  const renderList = keys.map((key, index) => {
    const id = `pseudo-select-${name}-${index}`;

    return (
      <li key={index} className={`PseudoSelect-item${selected === items[key] ? ' is-active' : ''}`}>
        <label className="PseudoSelect-label" htmlFor={id}>
          <input
            {...{ id, name }}
            value={items[key]}
            type="radio"
            defaultChecked={selected === items[key]}
            onClick={radioChange}
            className="PseudoSelect-radio"
          />
          <span className="PseudoSelect-text">{ key }</span>
        </label>
      </li>
    );
  });

  return (
    <div className="PseudoSelect">
      <ul className={`PseudoSelect-list${open ? ' is-open' : ''}`}>
        {renderList}
      </ul>
    </div>
  );
}
