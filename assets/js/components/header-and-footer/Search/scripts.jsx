import { ga } from 'react-ga';
import { h, render, Component } from 'preact';
import PropTypes from 'prop-types';
import queryString from 'query-string';
import Search from './index.jsx';
import { apiBaseURL } from '../../../utilities/config/global.json';
import removePunctuation from '../../../utilities/js/helpers/removePunctuation.js';


class SearchContainer extends Component {
  constructor(props) {
    super(props);

    // 'currentKeywords' indicates the current text the user typed in the search box
    // The second block contains factors that influence the UI state (searching means that UI is awaiting HTTP reponse for search suggestions)
    // The third block contains timeout specific variables (used when there is a delay/throttling in the UI)
    // The last block contains data that is retrieved from the HTTP request for search suggestions
    this.state = {
      currentKeywords: this.props.searchParam,

      focus: false,
      loading: false,
      searching: false,
      error: false,

      timeoutFocus: null,
      timeoutId: null,

      itemsArray: [],
      count: null,
    };

    this.findSuggestions = this.findSuggestions.bind(this);
    this.setFocus = this.setFocus.bind(this);
  }

  componentDidMount() {
    if (this.props.searchParam) {
      this.findSuggestions(this.state.currentKeywords);
    }
  }

  /**
   * Debounces setting the focus state of the search input (and subsequently the dropdown) by 500 miliseconds. This means that the search only closes if the mouse has left it for a minimum of 500 miliseconds.
   *
   * @param {boolean} value - Whether you want to set the focus on the search input to `true` or `false`.
   */
  setFocus(value) {
    return this.setState({ focus: value });
  }

  /**
   * Sends a HTTP get request to CKAN that checks if request returns a 200 or whether CKAN returns an error, if so resolves an JavaScript object. It also then logs these events retrospectively to Google Analytics (note the body reponse in an error is maxed at 500 characters). Once fetch is resolved it return an object that contains all the items capped at 10 (under `itemsArray`) and the amount in the CKAN database (under `count`).
   *
   * @param {string} newKeywords - The keywords that should be used to find suggested items. If not included the `currentKeywords` value in the state object will be used.
   *
   * @returns {*} - Returns a promise.
   */
  sendGetRequest(newKeywords = this.state.keywords) {
    const datasetPackagesQueryUrl = `${apiBaseURL}/api/3/action/package_search?q=${newKeywords}&start=0&rows=10&fq=+organization:national-treasury+vocab_financial_years:${this.props.selectedYear}+extras_department_name_slug:[* TO *]+extras_geographic_region_slug:[* TO *]`;
    const requestApi = this.props.requestOverride || datasetPackagesQueryUrl;


    return new Promise((resolve, reject) => {
      fetch(requestApi)
        .then((response) => {
          if (!response.ok) {
            response.text()
              .then((data) => {
                ga(
                  'send',
                  'event',
                  'search-error',
                  'error-response',
                  JSON.stringify({ url: response.url, body: data.slice(0, 500) }),
                );
              });

            reject(response);
          }

          response.json()
            .then((data) => {
              if (!data.success) {
                ga(
                  'send',
                  'event',
                  'search-error',
                  'ckan-200-error',
                  JSON.stringify({ url: response.url, error: data.error }),
                );
              }

              resolve({ itemsArray: data.result.results, count: data.result.count });
            })
            .catch(err => reject(err));
        })
        .catch(err => reject(err));
    });
  }

  /**
   * The wrapper method that executes the HTTP get request (via `this.sendGetRequest`) and sets the UI state accordingly. Note that method logs to the console an error under `console.warn` instead of throwing a traditional error. This is gracefully fail the request in the UI and to prevent an error from unwinding the stack should the HTTP request fail.
   *
   * @param {string} newKeywords - The keywords that should be used to find suggested items. If not included the `currentKeywords` value in the state object will be used.
   */
  findSuggestions(newKeywords) {
    this.setState({ currentKeywords: newKeywords });

    if (newKeywords.length >= 2) {
      clearTimeout(this.state.timeoutId);
      this.setState({ searching: true });
      this.setState({ count: null });

      const request = () => {
        return this.sendGetRequest(removePunctuation(newKeywords))
          .then(({ itemsArray, count }) => {
            this.setState({ count });
            this.setState({ timeoutId: null });
            this.setState({ itemsArray });
            this.setState({ searching: false });
          })
          .catch((err) => {
            this.setState({ searching: false });
            this.setState({ error: true });
            console.warn(err); // eslint-disable-line no-console
          });
      };

      const newTimeoutId = setTimeout(request, 1000);
      this.setState({ timeoutId: newTimeoutId });
    }
  }


  render() {
    return (
      <Search
        currentKeywords={this.state.currentKeywords}

        focus={this.state.focus}
        loading={this.state.loading}
        searching={this.state.searching}
        error={this.state.error}

        itemsArray={this.state.itemsArray}
        count={this.state.count}

        findSuggestions={this.findSuggestions}
        setFocus={this.setFocus}

        selectedYear={this.props.selectedYear}
      />
    );
  }
}


SearchContainer.propTypes = {
  searchParam: PropTypes.string,
  selectedYear: PropTypes.string.isRequired,
  requestOverride: PropTypes.string,
};

SearchContainer.defaultProps = {
  searchParam: '',
  requestOverride: null,
};


function scripts() {
  // Find all instances of a specific UI component on a page by parent class name.
  const componentsList = document.getElementsByClassName('js-initSearch');

  // Destructure needed query strings from URL
  const { search: searchParam, no_js: noJs } = queryString.parse(location.search) || {};

  if (componentsList.length > 0 && !noJs) {
    for (let i = 0; i < componentsList.length; i++) {
      // Find DOM node that will house the Preact app and get associated data attributes that are passed via HTML
      const component = componentsList[i];
      const requestOverride = component.getAttribute('data-request-override');
      const selectedYear = component.getAttribute('data-year');

      if (!selectedYear) {
        console.error("year data attribute not found in page.");
      }

      // Initialise Search Preact App
      render(
        <SearchContainer {...{ requestOverride, selectedYear, searchParam }} />,
        component,
      );
    }
  }
}


export default scripts();
