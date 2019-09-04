import { h } from 'preact';
import PropTypes from 'prop-types';
import TabSelection from './TabSelection.jsx';
import LandingLayout from './LandingLayout.jsx';
import FacetLayout from './FacetLayout.jsx';
import tabOptions from './../data/tabOptions.json';


/**
 *
 * @param props - Preact props object.
 * @param props.error - If true shows an error message instead of actual content.
 * @param props.loading - If true shows a loading spinner instead of actual content.
 * @param props.updateTab - Callback function that changes tab, sets {@link props.loading} to true
 * and sends HTTP request for data that will be needed on new tab.
 * @param props.addPage - Callback that just adds 5 new results to a facet tab.
 * @param props.tab - Determines what the current tab is, and therefore the layout to return.
 * @param props.year - Inserted into links and titles that are year specific.
 * @param props.response - The normalised response object passed to the presentation layer. Usually
 * contains a 'count' propery inidicating the total amount of search results returned and 'items'
 * that contains one or more lists of actual returned search results.
 * @param props.page - A value that is multiplied by 5 in order to determine how many results to
 * show on a facet page. Always resets to 1 when the tab is changed.
 */
function CalcContent(props) {
  const { error, loading } = props;
  const { updateTab, addPage } = props;
  const { tab, year, response, page } = props;
  const { count, items = {} } = response || {};

  if (error) {
    return (
      <div className="SearchResult-card is-dark u-marginTop25">
        <div className="SearchResult-cardTitle">Something went wrong</div>
        <div>Please try again at a later point.</div>
      </div>
    );
  }

  if (loading) {
    return <div className="Loader u-marginTop50 u-marginLeftAuto u-marginRightAuto" />;
  }

  if (count < 1) {
    return (
      <div className="SearchResult-card is-dark u-marginTop25">
        <div className="SearchResult-cardTitle">We found no results</div>
        <div>Try changing the searched year, or broaden your search terms.</div>
      </div>
    );
  }

  if (tab === 'all') {
    return <LandingLayout {...{ items, year, error, updateTab }} />;
  }

  return (
    <FacetLayout
      tab={tabOptions[tab]}
      tabKey={tab}
      {...{ addPage, page, year, error, count, response }} 
    />
  );
}


/**
 * Initialised the basic layout, with the title of the search term at the top of the page, and the
 * menu bar that allows you to switch between tabs. However loads another component that dynamically
 * determines what should be displayed in the content area.
 *
 * @param props - The Preact props object.
 * @param props.tab - The current displayed tab.
 * @param props.updateTab - A callback function enables the loading display, changes current tab and
 * fires new HTTP requests for the data needed for the new tab.
 * @param props.phrase - The search term as passed from the URL parameter.
 */
export default function SearchPage(props) {
  const { tab, updateTab, phrase } = props;
  return (
    <div className="SearchResult">
      <div className="Page-title u-textAlignCenter">Search results for &quot;{phrase}&quot;</div>
      <TabSelection {...{ tab, updateTab, tabOptions }} />
      <CalcContent {...props} />
    </div>
  );
}


const responseSchema = PropTypes.shape({
  count: PropTypes.number.isRequired,
  items: PropTypes.objectOf(
    PropTypes.shape({
      count: PropTypes.number.isRequired,
      items: PropTypes.shape({
        title: PropTypes.string.isRequired,
        url: PropTypes.string.isRequired,
        contributor: PropTypes.string.isRequired,
        snippet: PropTypes.string,
        source: {
          url: PropTypes.string,
          text: PropTypes.string,
        },
      }),
    }),
  ),
});

SearchPage.propTypes = {
  tab: PropTypes.oneOf(['all', 'contributed', 'national', 'provincial']).isRequired,
  updateTab: PropTypes.func.isRequired,
  phrase: PropTypes.string.isRequired,
  error: PropTypes.bool,
  loading: PropTypes.bool,
  addPage: PropTypes.func,
  year: PropTypes.string.isRequired,
  page: PropTypes.number.isRequired,
};


SearchPage.defaultProps = {
  error: false,
  loading: false,
  addPage: null,
  response: {},
};
