import fetchWrapper from './../../../../utilities/js/helpers/fetchWrapper.js';
import normaliseServerResponse from './normaliseServerResponse.js';
import highlightResults from './highlightResults.js';
import createPromiseToken from './../../../../utilities/js/helpers/createPromiseToken.js';
import parseStaticResponse from './parseStaticResponse.js';


export default function getLandingResults(phrase, year) {
  const normaliseOtherYears = (response, tab) => {
    const { items } = response.result.search_facets.vocab_financial_years;
    return items.reverse().map(({ count, name }) => {
      const url = `/${name}/search-result?search=${phrase}&view=${tab}`;

      return {
        count,
        name,
        url,
      };
    });
  };


  const request = new Promise((resolve, reject) => {
    const urlsArray = [
      `https://data.vulekamali.gov.za/api/3/action/package_search?q=${encodeURI(phrase)}&start=0&rows=3&fq=+organization:national-treasury+vocab_financial_years:${year}+groups:"budget-vote-documents"+extras_department_name_slug:[*%20TO%20*]+extras_geographic_region_slug:[*%20TO%20*]&ext_highlight=true`,

      `https://data.vulekamali.gov.za/api/3/action/package_search?q=${encodeURI(phrase)}&start=0&rows=0&fq=+organization:national-treasury+groups:"budget-vote-documents"+extras_department_name_slug:[*%20TO%20*]+extras_geographic_region_slug:[*%20TO%20*]&facet.field=[%22vocab_financial_years%22]`,

      `https://data.vulekamali.gov.za/api/3/action/package_search?q=${encodeURI(phrase)}&start=0&rows=3&fq=-organization:national-treasury%20AND%20NOT%20groups:[%22%22%20TO%20*]&ext_highlight=true`,

      `https://data.vulekamali.gov.za/api/3/action/package_search?q=${encodeURI(phrase)}&start=0&rows=3&fq=groups:[%22%22%20TO%20*]-groups:"budget-vote-documents"-groups:"adjusted-budget-vote-documents"&ext_highlight=true`,

      '/json/static-search.json',
    ];


    Promise.all(urlsArray.map(fetchWrapper))
      .then((returnArr) => {
        const [
          rawDepts,
          rawDeptsOtherYears,
          rawContributed,
          rawDatasets,
          staticContent,
        ] = returnArr;

        const resultsArr = [rawDepts, rawContributed, rawDatasets].map(normaliseServerResponse);
        const [depts, contributed, datasets] = resultsArr.map((item) => {
          return highlightResults(item, phrase);
        });

        const deptsOtherYears = normaliseOtherYears(rawDeptsOtherYears, 'departments');
        const { videos, glossary } = parseStaticResponse(phrase, staticContent.videos, staticContent.glossary);

        resolve(
          {
            items: {
              departments: {
                ...depts,
                otherYears: deptsOtherYears,
              },
              datasets,
              contributed,
              videos,
              glossary,
            },
            count: depts.count + contributed.count,
          },
        );
      })
      .catch(reject);
  });

  return createPromiseToken(request);
}
