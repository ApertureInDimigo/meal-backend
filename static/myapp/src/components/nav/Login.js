import React, {useContext, useEffect, useState} from "react";

import styled from 'styled-components';

import {Redirect, withRouter} from "react-router-dom";
import {getToken, GetMyIdentity} from "../../api/Auth";

import {setCookie, removeCookie} from "../../lib/cookie"

import {UserContext} from "../../contexts/UserContext"


const Login = props => {
    const userInfo = useContext(UserContext).info;
    if (userInfo.id) {
        return <Redirect to={"/"}/>
    }

    const handleSubmit = e => {
        e.preventDefault(); // 기본적인 서브밋 행동을 취소합니다

        // Submit후 하고싶은 것을 적어주세요!
        LoginHandler()


    }

    const LoginHandler = async () => {

        console.log(id, password)
        let query = {"id": id, "password": password}


        const response = await getToken(query);
        console.log(response)

        switch (response.status) {
            case 404:
                removeCookie('access_token')
                alert("ID 또는 비밀번호 틀림")
                break
            case 200:
                setCookie('access_token', response.data.accessToken, '3');
                props.history.push('/')
                alert(`로그인 성공~`)
                break
        }


    };

    const GetMyIdentityHandler = async () => {
        const response2 = await GetMyIdentity();
        console.log(response2)
    }

    const [id, setId] = useState('');
    const [password, setPassword] = useState('');
    return (
        <div>
            <form onSubmit={handleSubmit}>
                아이디 <input value={id} onInput={e => setId(e.target.value)}/>
                비번 <input type="password" value={password} onInput={e => setPassword(e.target.value)}/>
                <button>로그인</button>
            </form>

        </div>


    )
};

export default withRouter(Login);
