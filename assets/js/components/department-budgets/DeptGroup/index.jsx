import GovernmentResources from './../../GovernmentResources/GovernmentResources.jsx';

import Map from './partials/Map.jsx';

function notAvailableMessage() {
  return (
    <div>
      <p className="u-fontStyle u-fontStyle--italic">This data is not yet available. Provincial budgets are tabled after the national budget has been announced. This is because the national budget determines the amount of money each province receives. We expect to be able make provincial budget data available by April {(new Date()).getFullYear()}.</p>
      <p>{"In the meantime you view previous financial years' data by selecting a year at the top of your screen."}</p>
    </div>
  );
}

function departments(linksArray, doubleRow) {
  return (
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
  )
}

export default function DeptGroup({ map, linksArray, label, name, doubleRow, empty, govResourceGroups }) {
  return (
    <div>
      <div className="DeptGroup">
        <div className="DeptGroup-mapWrap">
          <div className="DeptGroup-wrap">
            <h3 className="DeptGroup-title">{label} Department Budgets</h3>
            {empty ? notAvailableMessage() : departments(linksArray, doubleRow)}
          </div>
          <div className="DeptGroup-map">
            {Map(map)}
          </div>
        </div>
        <GovernmentResources title={label} govResourceGroups={govResourceGroups} />
      </div>
    </div>
  );
}
