import React from 'react';
import { storiesOf } from '@storybook/react';
import Homepage from './index';


const beforeSpeechProps = {
  image: 'parliament',
  heading: 'New budget data will be available soon',
  subheading: 'The 2019 budget speech',
  buttons: {
    primary: {
      text: 'How to watch the speech',
    },
    secondary: {
      text: 'Get notified when data is live',
      link: '#',
    },
  },
  notice: 'The 2019/20 budget will be live on Vulekamali by 22 February 2019.',
};

const duringSpeechProps = {
  image: 'https://via.placeholder.com/150',
  heading: 'New budget data will go live soon',
  subheading: 'The 2019 budget speech has commenced',
  buttons: {
    primary: {
      text: 'Watch the speech',
      link: 'http://www.treasury.gov.za/documents/national%20budget/2019/webcast.aspx'
    },
    secondary: {
      text: 'Download budget resources',
      link: '#',
    },
  },
  notice: 'The 2019/20 budget will be live on Vulekamali by 22 February 2019.',
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


const beforeSpeech = () => <Homepage {...beforeSpeechProps} />;
const duringSpeech = () => <Homepage {...duringSpeechProps} />;


storiesOf('views.Homepage', module)
  .add('Before Speech', beforeSpeech)
  .add('During Speech', duringSpeech);
