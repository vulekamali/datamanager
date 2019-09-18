import fetchWrapper from './../../../../utilities/js/helpers/fetchWrapper.js';
import normaliseServerResponse from './normaliseServerResponse.js';
import highlightResults from './highlightResults.js';
import createPromiseToken from './../../../../utilities/js/helpers/createPromiseToken.js';


const buildUrl = (phrase, start, facet, year) => {
  if (facet === 'contributed') {
    return `https://data.vulekamali.gov.za/api/3/action/package_search?q=${encodeURI(phrase)}&start=${start}&rows=5&fq=-organization:national-treasury%20AND%20NOT%20groups:[%22%22%20TO%20*]&ext_highlight=true`;
  }

  if (facet === 'datasets') {
    return `https://data.vulekamali.gov.za/api/3/action/package_search?q=${encodeURI(phrase)}&start=${start}&rows=5&fq=groups:[%22%22%20TO%20*]-groups:"budget-vote-documents"-groups:"adjusted-budget-vote-documents"&ext_highlight=true`;
  }

  return `https://data.vulekamali.gov.za/api/3/action/package_search?q=${encodeURI(phrase)}&start=${start}&rows=5&fq=+organization:national-treasury+vocab_financial_years:${year}+groups:"budget-vote-documents"+extras_department_name_slug:[*%20TO%20*]+extras_geographic_region_slug:[*%20TO%20*]&ext_highlight=true`;
};


export default function getFacetResults(phrase, facet, start = 0, year) {
  const request = new Promise((resolve, reject) => {
    const innerRequest = fetchWrapper(buildUrl(phrase, start, facet, year));

    innerRequest
      .then((data) => {
        const results = normaliseServerResponse(data, facet);
        const output = highlightResults(results, phrase);

        resolve({
          count: output.count,
          [facet]: output,
        });
      })
      .catch(reject);
  });

  return createPromiseToken(request);
}
