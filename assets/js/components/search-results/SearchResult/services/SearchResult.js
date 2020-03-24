import { createElement, Component } from 'preact';
import getLandingResults from './getLandingResults.js';
import getFacetResults from './getFacetResults.js';
import SearchPage from './../presentation/SearchPage.jsx';
import getCkanUrl from './../../../../utilities/config/siteConfig.js';


export default class SearchPageContainer extends Component {
  constructor(props) {
    super(props);
    const { view } = this.props;

    this.state = {
      tab: view || 'all',
      items: {},
      loading: true,
      error: false,
      loadingPage: false,
      page: 1,
      ckanUrl: getCkanUrl(),
    };

    this.static = {
      currentFetch: null,
    };

    this.events = {
      updateTab: this.updateTab.bind(this),
      addPage: this.addPage.bind(this),
    };
  }

  componentWillMount() {
    const { search: phrase, view = 'all', year } = this.props;

    this.setState({
      loading: true,
      tab: view,
    });

    if (view === 'all') {
      const callbackWrap = () => getLandingResults(this.state.ckanUrl, phrase, year);
      return this.getNewResults(phrase, view, callbackWrap);
    }

    const callbackWrap = () => getFacetResults(this.state.ckanUrl, phrase, view, 0, year);
    return this.getNewResults(phrase, view, callbackWrap);
  }


  getNewResults(phrase, newTab, callback) {
    if (this.static.currentFetch && this.static.currentFetch.token.active) {
      this.static.currentFetch.token.cancel();
    }

    this.static.currentFetch = callback();

    this.static.currentFetch.request
      .then(items => this.setState({
        items,
        loading: false,
      }))
      .catch((err) => {
        this.setState({
          error: true,
          loading: false,
        });
        console.warn(err);
      });
  }


  addPage() {
    const { tab, page, items } = this.state;
    const { search: phrase, year } = this.props;

    if (this.static.currentFetch && this.static.currentFetch.token.active) {
      this.static.currentFetch.token.cancel();
    }

    this.static.currentFetch = getFacetResults(this.state.ckanUrl, phrase, tab, page * 5, year);

    this.static.currentFetch.request
      .then((data) => {
        const newTab = {
          ...items,
          items: [
            ...items[tab].items,
            ...data[tab].items,
          ],
        };

        this.setState({
          page: page + 1,
          items: {
            [tab]: newTab,
            count: items.count,
          },
        });
      })
      .catch((err) => {
        this.setState({
          error: true,
          loading: false,
        });
        console.warn(err);
      });
  }


  updateTab(newTab, scroll) {
    const { search: phrase, year, root } = this.props;
    const { tab } = this.state;

    this.setState({
      tab: newTab,
      loading: true,
      page: 1,
      items: null,
    });

    if (scroll) {
      root.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    history.replaceState({}, '', `/${year}/search-result?search=${encodeURI(phrase)}&view=${newTab}`);

    if (newTab === 'all') {
      const callbackWrap = () => getLandingResults(this.state.ckanUrl, phrase, year);
      return this.getNewResults(phrase, newTab, callbackWrap);
    }

    const callbackWrap = () => getFacetResults(this.state.ckanUrl, phrase, newTab, 0, year);
    return this.getNewResults(phrase, newTab, callbackWrap);
  }


  render() {
    const { search: phrase, year } = this.props;
    const { tab, items: response, loading, loadingPage, page, error } = this.state;

    const { updateTab, addPage } = this.events;

    return createElement(
      SearchPage,
      {
        phrase,
        page,
        response,
        tab,
        year,
        updateTab,
        loading,
        addPage,
        loadingPage,
        error,
      },
    );
  }
}
