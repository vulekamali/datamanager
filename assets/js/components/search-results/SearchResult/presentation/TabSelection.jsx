import React from 'react';


export default function TabSelection({ tab, updateTab, tabOptions }) {
  const items = Object.keys(tabOptions).map((key) => {
    const value = tabOptions[key];
    const className = [
      'SearchResult-tabItem',
      (key === tab ? 'is-active' : ''),
    ].join(' ');
    const updateTabWrap = () => updateTab(key);

    return <button {...{ className, key }} onClick={updateTabWrap}>{value}</button>;
  });

  return (
    <div className="SearchResult-tabWrap">
      <div className="SearchResult-tabList">
        {items}
      </div>
    </div>
  );
}