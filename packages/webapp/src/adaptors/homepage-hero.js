import { createElement } from 'react';
import { render } from 'react-dom';
import Homepage from '../views/Homepage';


const props = {
  image: 'https://via.placeholder.com/150',
  heading: 'New budget data is now live!',
  subheading: 'The 2019 budget speech has been completed.',
  buttons: {
    primary: {
      text: 'Select a department',
      link: '/2019-20/departments'
    },
    secondary: {
      text: 'Download budget resources',
      link: '#',
    },
  },
  callToAction: {
    subheading: 'Budget feature',
    heading: 'The Status of National Department Infrastructure Projects in South Africa',
    link: {
      text: 'Read this feature',
      link: 'https://vulekamali.gov.za/infrastructure-projects',
    },
  },
  resources: [
    {
      heading: 'Budget Speech',
      size: '0.4MB',
      format: 'PDF',
      link: 'http://www.treasury.gov.za/documents/national%20budget/2019/speech/speech.pdf',
    },
    {
      heading: 'Budget Review',
      size: '10.7MB',
      format: 'PDF',
      link: 'http://www.treasury.gov.za/documents/national%20budget/2019/review/FullBR.pdf',
    },
    {
      heading: 'Budget Revenue Data',
      size: '0.03MB',
      format: 'XLSX',
      link: 'http://www.treasury.gov.za/documents/national%20budget/2019/TimeSeries/Excel/Table%202%20-%20Main%20budget%20estimates%20of%20national%20revenue.xlsx',
    },
    {
      heading: 'Estimates National Expenditure',
      size: '10.2MB',
      format: 'PDF',
      link: 'http://www.treasury.gov.za/documents/national%20budget/2019/ene/FullENE.pdf',
    },
    {
      heading: 'Estimates National Expenditure Data',
      size: '0.14MB',
      format: 'ZIP',
      link: 'http://www.treasury.gov.za/documents/national%20budget/2019/ene/ENE%20Summary%20Tables.zip',
    },
    {
      heading: 'Division Revenue Bill',
      size: '4MB',
      format: 'PDF',
      link: 'http://www.treasury.gov.za/legislation/bills/2019/[B5-2019]%20(Division%20of%20Revenue).pdf',
    },
    {
      heading: 'Budget Highlights',
      size: '0.14MB',
      format: 'PDF',
      link: 'http://www.treasury.gov.za/documents/national%20budget/2019/sars/Budget%202019%20Highlights.pdf',
    },
    {
      heading: 'Appropriation Bill',
      size: '0.56MB',
      format: 'PDF',
      link: 'http://www.treasury.gov.za/legislation/bills/2019/[B6-2019]%20(Appropriation).pdf',
    },
    {
      heading: 'Pocket Guide',
      size: '0.45MB',
      format: 'PDF',
      link: 'http://www.treasury.gov.za/documents/national%20budget/2019/sars/Budget%202019%20Tax%20Guide.pdf',
    },
    {
      heading: 'People Guide (Afrikaans)',
      size: '2.47MB',
      format: 'PDF',
      link: 'http://www.treasury.gov.za/documents/national%20budget/2019/guides/2019%20Peoples%20Guide%20Afrikaans.pdf',
    },
    {
      heading: 'People Guide (English)',
      size: '2.42MB',
      format: 'PDF',
      link: 'http://www.treasury.gov.za/documents/national%20budget/2019/guides/2019%20Peoples%20Guide%20English.pdf',
    },
    {
      heading: 'People Guide (Setswana)',
      size: '2.41MB',
      format: 'PDF',
      link: 'http://www.treasury.gov.za/documents/national%20budget/2019/guides/2019%20Peoples%20Guide%20Setswana.pdf',
    },
    {
      heading: 'People Guide (Xhosa)',
      size: '2.23MB',
      format: 'PDF',
      link: 'http://www.treasury.gov.za/documents/national%20budget/2019/guides/2019%20Peoples%20Guide%20Xhosa.pdf',
    },
    {
      heading: 'People Guide (Zulu)',
      size: '2.19MB',
      format: 'PDF',
      link: 'http://www.treasury.gov.za/documents/national%20budget/2019/guides/2019%20Peoples%20Guide%20Zulu.pdf',
    },
    {
      heading: 'All Resources',
      size: null,
      format: 'Web',
      link: 'http://www.treasury.gov.za/documents/national%20budget/2019/default.aspx',
    },
  ],
};

const node = document.querySelector('[data-webapp="homepage-hero"]')

const connection = () => {
  if (node) {
    render(createElement(Homepage, props), node);
  }
};

export default connection();
