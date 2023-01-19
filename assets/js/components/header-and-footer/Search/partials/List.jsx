import PropTypes from 'prop-types';


export default function List(props) {
  const {
    count,
    currentKeywords,
    error,
    itemsArray,
    searching,
    selectedYear,
  } = props;


  // ...
  const getExtraValue = (extras, key) => {
    const index = extras.findIndex(data => data.key === key);
    return extras[index].value;
  };


  // ...
  const buildGaQuery = () => {
    return `?search_type=suggestion-click&search_string=${selectedYear}%3A%20${currentKeywords}`;
  };


  // ...
  const generateDeptName = (item) => {
    const isNational = item.province.length > 0;
    return isNational ? item.province : 'National';
  };


  // ...
  const generateUrl = (item) => {
    const provSlug = getExtraValue(item.extras, 'geographic_region_slug');
    const nameSlug = getExtraValue(item.extras, 'department_name_slug');

    const baseUrl = provSlug === 'south-africa' ?
      `/${selectedYear}/national/departments/${nameSlug}` :
      `/${selectedYear}/provincial/${provSlug}/departments/${nameSlug}`;

    return baseUrl + buildGaQuery(selectedYear, currentKeywords);
  };


  // ...
  const searchingMarkup = (
    <div className="Search-list">
      <div className="Search-loading">
        Searching...
      </div>
    </div>
  );


  // ...
  const errorMarkup = (
    <div className="Search-list">
      <div className="Search-error">
        <span>Something went wrong with the search. Please try again at a later point.</span>
      </div>
    </div>
  );


  // ...
  const emptyMarkup = (
    <div className="Search-list">
      <div className="Search-error">
        <span>We didn&#8217;t find anything for &#8217;{ currentKeywords }&#8217;. </span>
        <a href={`/${selectedYear}/departments${buildGaQuery(selectedYear, currentKeywords)}`}>
          View a list of all departments
        </a>
      </div>
    </div>
  );


  // ...
  const itemMarkup = () => {
    const result = itemsArray.map((item) => {
      return (
        <li>
          <a href={generateUrl(item)} className="Search-link">
            {generateDeptName(item)} Department: {getExtraValue(item.extras, 'Department Name')}
          </a>
        </li>
      );
    });

    return (
      <ul className="Search-list">
        {result}
      </ul>
    );
  };


  // ...
  const buildList = () => {
    if (searching) {
      return searchingMarkup;
    }

    if (error) {
      return errorMarkup;
    }

    if (itemsArray.length < 1) {
      return emptyMarkup;
    }

    return itemMarkup();
  };


  // ...
  const formatCount = (fnCount) => {
    if (!fnCount) {
      return null;
    }

    return ` (Showing ${fnCount < 10 ? fnCount : 10} of ${fnCount})`;
  };


  return (
    <div>
      <span className="Search-title">
        <span>Suggested Department Budgets</span>
        <span className="Search-showing">
          {formatCount(count)}
        </span>
      </span>
      { buildList() }
    </div>
  );
}


List.propTypes = {
  count: PropTypes.string.isRequired,
  currentKeywords: PropTypes.string.isRequired,
  error: PropTypes.bool.isRequired,

  itemsArray: PropTypes.arrayOf(
    PropTypes.shape({
      sphere: PropTypes.arrayOf(PropTypes.string),
      financial_year: PropTypes.arrayOf(PropTypes.string),
      extras: PropTypes.arrayOf(
        PropTypes.shape({
          key: PropTypes.string,
          value: PropTypes.string,
        }),
      ),
    }),
  ),

  searching: PropTypes.bool.isRequired,
  selectedYear: PropTypes.string.isRequired,
};


List.defaultProps = {
  itemsArray: [],
};
