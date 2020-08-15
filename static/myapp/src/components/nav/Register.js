import React, {useContext, useEffect, useState} from "react";
import {useReducer} from 'react';
import styled from 'styled-components';

import {Redirect, withRouter} from "react-router-dom";
import {register} from "../../api/Users";
import {UserContext} from "../../contexts/UserContext";


function reducer(state, action) {
    return {
        ...state,
        [action.name]: action.value
    };
}


const Register = props => {
    const userInfo = useContext(UserContext).info;
    if (userInfo.id) {
        return <Redirect to={"/"}/>
    }

    const handleSubmit = e => {
        e.preventDefault();

        RegisterHandler()


    }

    const RegisterHandler = async () => {

        console.log(id, password)
        let query = {"id": id, "password": password, "nickname": nickname}


        const response = await register(query);
        console.log(response)

        switch (response.status) {
            case 409:
                alert("중복")
                break
            case 400:
                alert("파라미터 무효")
                break
            case 201:
                props.history.push('/login')
                alert(`횐가입 성공`)
                break
        }


    };

    const GetMyIdentityHandler = async () => {
        const response2 = await GetMyIdentity();
    }

    const [state, dispatch] = useReducer(reducer, {
        id: '',
        password: '',
        nickname: ''
    });
    const {id, password, nickname} = state;
    const onChange = e => {
        dispatch(e.target);
    };
    return (
        <div>
            <form onSubmit={handleSubmit}>
                아이디 <input name="id" value={id} onChange={onChange}/>
                비번 <input type="password" name="password" value={password} onChange={onChange}/>
                이름 <input name="nickname" value={nickname} onChange={onChange}/>
                <button>회원가입</button>
            </form>

        </div>


    )
};

export default withRouter(Register);
