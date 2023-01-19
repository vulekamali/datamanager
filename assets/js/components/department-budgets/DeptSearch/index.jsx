import DeptControl from './../DeptControl/index.jsx';
import DeptGroup from './../DeptGroup/index.jsx';


const makeGroup = (slug, departments, name, label, empty, govResourceGroups) => {
  return (
    <div className="DeptSearch-groupWrap">
      <DeptGroup
        map={slug}
        linksArray={departments}
        label={label}
        name={name}
        empty={empty}
        doubleRow={slug === 'south-africa'}
        govResourceGroups={govResourceGroups}
      />
    </div>
  );
};


const emptyNotification = (
  <div className="Section is-bevel is-dark">
    <div className="Section-card is-invisible">
      <div className="Section-title">
        No results found
      </div>
      <div>
        Please try changing or broadening your search terms
      </div>
    </div>
  </div>
);


const makeGroups = (governments, resourceGroups) => {
  const hasItemsInDept = ({ departments }) => departments.length > 0;

  if (governments.filter(hasItemsInDept).length < 1) {
    return emptyNotification;
  }

  return governments.map(
    ({ name, slug, departments, label }) => {
      const empty = departments.length == 0;
      return makeGroup(slug, departments, name, label, empty, resourceGroups[name]);
    },
  );
};


function DeptSearch({ state, eventHandlers }) {

  return (
    <div className="DeptSearch">
      <div className="DeptSearch-wrap">
        <h3 className="u-sReadOnly">Filters</h3>
        <ul className="DeptSearch-list">
          <li>
            <DeptControl
              open={state.open}

              keywords={state.filters.keywords}
              sphere={state.filters.sphere}
              province={state.filters.province}

              updateFilter={eventHandlers.updateDropdown}
              changeKeywords={eventHandlers.updateKeywords}
            />
          </li>
        </ul>
        <h3 className="u-sReadOnly">Results</h3>
        <div className="DeptSearch-results">
          {makeGroups(state.results, state.resourceGroups)}
        </div>
      </div>
    </div>
  );
}

export { DeptSearch, makeGroups };
