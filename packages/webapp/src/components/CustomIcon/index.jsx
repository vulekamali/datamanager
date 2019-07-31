import { SvgIcon } from '@material-ui/core';
import React from 'react';

import Family from './Family';
import Plant from './Plant';
import Shield from './Shield';
import Dollar from './Dollar';
import Money from './Money';
import Growth from './Growth';
import Health from './Health';
import Education from './Education';
import Tap from './Tap';
import Community from './Community';
import Police from './Police';
import Person from './Person';
import Training from './Training';

const returnContent = type => {
  switch (type) {
    case 'family':
      return <Family />;
    case 'plant':
      return <Plant />;
    case 'shield':
      return <Shield />;
    case 'dollar':
      return <Dollar />;
    case 'money':
      return <Money />;
    case 'growth':
      return <Growth />;
    case 'health':
      return <Health />;
    case 'education':
      return <Education />;
    case 'tap':
      return <Tap />;
    case 'community':
      return <Community />;
    case 'police':
      return <Police />;
    case 'person':
      return <Person />;
    case 'training':
      return <Training />;
    default:
      return null;
  }
};

const CustomIcon = ({ type, ...props }) => <SvgIcon {...props}>{returnContent(type)}</SvgIcon>;

export default CustomIcon;
