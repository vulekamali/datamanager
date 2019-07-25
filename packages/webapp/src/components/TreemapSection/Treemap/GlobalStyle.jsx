import { createGlobalStyle } from 'styled-components';

const GlobalStyle = createGlobalStyle`
  rect:hover {
    opacity: 0.9;
  }

  text.name {
    font-family: Roboto, sans-serif;
    fill: black;
    font-size: 16px;
    font-weight: bold;
  }
  text.amount {
    font-family: Roboto, sans-serif;
    fill: black;
    font-size: 16px;
    font-weight: bold;
  }

  svg {
    width: 100%;
    height: 100%;
    border-radius: 10px;
  }
`;

export default GlobalStyle;
