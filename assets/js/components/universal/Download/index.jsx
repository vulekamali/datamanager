import React from 'react';
import Icon from '../../Icon/index.jsx';


export default function Download({ link, title, icon }) {
  const iconSection = (
    <span className="Download-icon">
      <Icon type="download" size="xs" />
    </span>
  );

  return (
    <a href={link} className="Download" rel="noopener noreferrer" target="_blank">
      {icon ? iconSection : null}
      <span>{title}</span>
    </a>
  );
}
