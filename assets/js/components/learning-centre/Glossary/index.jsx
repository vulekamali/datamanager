import React from 'react';
import Controls from './partials/Controls.jsx';
import List from './partials/List.jsx';

export default function Markup({ currentPhrase, currentItems, changePhrase }) {
  return (
    <div className="Glossary-wrap">
      <Controls {...{ currentPhrase, currentItems, changePhrase }} />
      <List {...{ currentItems }} />
    </div>
  );
}
