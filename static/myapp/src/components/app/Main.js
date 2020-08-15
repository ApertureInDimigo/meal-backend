import React, {useEffect, useState} from "react";
import './Main.css'



import {withRouter} from "react-router-dom";


const Main = props => {

    const [text, setText] = useState("");



    const onTextUpdate = e => {
        setText(e.target.value);
    };


    return (

        <div style={{"display": "flex", "font-size": "45px", "text-align": "center"}}>
            <div style={{"flex" : "none", "margin" : "auto"}}>
                <div>메인 화면 입니다!</div>
                <input onChange={onTextUpdate}/>
                <div>
                    {text}
                </div>
            </div>

        </div>
    );
};
//aa
export default withRouter(Main);
