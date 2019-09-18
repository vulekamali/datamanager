import {
  Typography,
  Select,
} from '@material-ui/core';

import styled from 'styled-components';

const Wrapper = styled.div`
  background: #f4f4f4;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 50px 20px;
`;

const ResourceWrapper = styled.div`
  max-width: 1000px;
`;

const Heading = styled(Typography)`
&& {
  text-align: center;
  text-transform: uppercase;
  font-size: 14px;
  letter-spacing: 3px;
  padding: 10px;
}
`;


export {
  Wrapper,
  ResourceWrapper,
  Heading
}

export default {
  Wrapper,
  ResourceWrapper,
  Heading
}
