import React, {useEffect, useState, useContext} from "react";


import styled from 'styled-components';

import {withRouter, Link} from "react-router-dom";

import {getCookie, removeCookie} from "../../lib/cookie"
import {parseJwt} from "../../lib/login";
import {GetMyIdentity} from "../../api/Auth"

import {SampleConsumer} from "../../contexts/sample";

import {UserContext} from "../../contexts/UserContext"

const Navbar = props => {

    const NavContainer = styled.div`
    display : flex;
    height : 45px;
    background-color:#fafafa;
    `


    const NavItems = styled.div`
    flex : none;
    ${props => {
        if (props.right) {
            return `margin-left : auto;`;
        }
    }}
    `

    const NavItem = styled.div`
    line-height : 45px;
    text-align:center;
    border-radius : 5px;
    border : 1px solid gray;
    display : inline-block;
    padding : 0px 15px;
    background-color : white;
    `


    const userInfo = useContext(UserContext);
    const {setState} = useContext(UserContext);


    const [isLogin, setIsLogin] = useState(false);

    useEffect(() => {


        async function getIsLogin() {
            let response = await GetMyIdentity()


            switch (response.status) {
                case 200:
                    console.log(response.data.data)
                    let data = response.data.data
                    setIsLogin(true)
                    // setUserData(data)
                    setState(data)
                    break
                case 400:
                case 401:
                    setIsLogin(false)
                    break
            }
        }

        getIsLogin()


    }, [props.location.key]);

    const logout = () => {
        removeCookie('access_token')
        let data = {"id": undefined, "nickname": undefined}
        // setUserData(data)
        setState(data)
        props.history.push('/')
    }

    return (
        <NavContainer style={{"display": "flex"}}>

            <NavItems>
                <NavItem>
                    <Link to={"/"}>멋진 로고</Link>
                </NavItem>

            </NavItems>


            {
                isLogin &&

                <NavItems right>
                    <NavItem>
                        {userInfo.info.nickname}
                    </NavItem>
                    <NavItem onClick={logout}>
                        로그아웃
                    </NavItem>
                </NavItems>
            }
            {
                !isLogin &&
                <NavItems right>
                    <NavItem>
                        <Link to={"/register"}>회원가입</Link>
                    </NavItem>
                    <NavItem>
                        <Link to={"/login"}>로그인</Link>
                    </NavItem>
                </NavItems>
            }


        </NavContainer>
    )
};

export default withRouter(Navbar);
