import { h } from 'preact';
import GovernmentResources from './../../GovernmentResources/GovernmentResources.jsx';

import Map from './partials/Map.jsx';

export default function DeptGroup({ map, linksArray, name: title, doubleRow, empty }) {

  if (empty) {
    return (
      <div className="DeptGroup">
        <div className="DeptGroup-wrap">
          <h3 className="DeptGroup-title">{title} Department Budgets</h3>
          <p className="u-fontStyle u-fontStyle--italic">This data is not yet available. Provincial budgets are tabled after the national budget has been announced. This is because the national budget determines the amount of money each province receives. We expect to be able make provincial budget data available by April {(new Date()).getFullYear()}.</p>
          <p>{"In the meantime you view previous financial years' data by selecting a year at the top of your screen."}</p>
        </div>
        <div className="DeptGroup-map">
          {Map(map)}
        </div>
      </div>
    );
  }

  return (
    <div className="DeptGroup">
      <div className="DeptGroup-wrap">
        <h3 className="DeptGroup-title">{title} Department Budgets</h3>
        <ul className={`DeptGroup-list${doubleRow ? ' DeptGroup-list--doubleRow' : ''}`}>
          {
            linksArray.map(({ name, url_path: url }) => {
              return (
                <li className="DeptGroup-item">
                  <a className="DeptGroup-link" href={url} dangerouslySetInnerHTML={{ __html: name }} />
                </li>
              );
            })
          }
        </ul>
      </div>
      <div className="DeptGroup-map">
        {Map(map)}
      </div>
      <div>{"hello there"}</div>
      <GovernmentResources title={title} />
      <div>{"bye now"}</div>
    </div>
  );
}
