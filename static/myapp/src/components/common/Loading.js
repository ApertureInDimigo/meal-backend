import React from "react";
import { css } from "@emotion/core";
// First way to import
//import { ClipLoader } from "react-spinners";
// Another way to import. This is recommended to reduce bundle size
import SyncLoader from "react-spinners/SyncLoader";
import {withRouter} from "react-router-dom";

// Can be a string as well. Need to ensure each key-value pair ends with ;
const override = css`

  display: block;
  margin: 30px;
  border-color: red;
  text-align:center;
  
`;

class Loading extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loading: true
    };
  }

  render() {

    return (
      <div className="sweet-loading">
        <SyncLoader
          css={override}
          size={15}
          //size={"150px"} this also works
          color={"#50E3C2"}
          loading={this.props.loading}
        />
      </div>
    );
  }
}

export default Loading;