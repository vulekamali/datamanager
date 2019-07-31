import Button from '@material-ui/core/Button';
import styled from 'styled-components';
import { darken } from 'polished';


const PrimaryButton = styled(Button)`
  && {
    background: #79b443;
    border-radius: 50px;
    color: white;
    text-transform: none;
    padding: 10px 25px;
    font-family: Lato;
    font-size: 16px;
    font-weight: 700;
    box-shadow: none;

    &:hover {
      background: ${darken(0.1, '#79B443')};
    }
  }
`;


const SecondaryButton = styled(PrimaryButton)`
  && {
    background: #161616;

    &:hover {
      background: ${darken(0.1, '#161616')};
    }
  }
`;


export {
  PrimaryButton,
  SecondaryButton,
}

export default {
  PrimaryButton,
  SecondaryButton,
}