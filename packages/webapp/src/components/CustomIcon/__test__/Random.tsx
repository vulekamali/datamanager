import React from 'react';
import { mockProps, Tprops } from '../schema';
import CustomIcon from '../index';

const passedProps: Tprops = mockProps();

const Test = () => <CustomIcon {...passedProps} />;

export default Test;
