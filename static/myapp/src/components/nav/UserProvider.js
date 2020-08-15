import React, { useState } from "react";
import {UserContext} from "../../contexts/UserContext"

//이 페이지의 특징은 함수같은 것들을 먼저 정의하고
//useState를 통한 state 및 setState를 나중에 했다는 것입니다.
//여기서 Hook에 관한 이해가 필요합니다.
//생각보다 바로 이해하기 어려우니 심사숙고하며 보는걸 추천합니다.

//사용하고자 하는 컴포넌트 최상위에 지정할 Provider컴포넌트 입니다.
export const UserProvider = ({ children }) => {

//우리가 Blue에서 사용할 함수입니다.
  const increase = () => {
//그 함수안에서 Hooks의 setNumber()를 사용 했습니다.
//prevState를 받아서 return을 통해 state를 업데이트 합니다.
    setNumber(prevState => {
      return {
        ...prevState,
        number: prevState.number + 1
      };
    });
  };

  const decrease = () => {
    setNumber(prevState => {
      return {
        ...prevState,
        number: prevState.number - 1
      };
    });
  };
   const setState = (state) => {
    setInfo(prevState => {
      return {
        ...prevState,
        info : state
      };
    });
  };

//state초기화 객체 입니다.
  const initialState = {
    info: {"id":"", "nickname" : ""},
    increase,
    decrease,
    setState
  };
//Hook을 통한 state, setState를 정의합니다.
  const [info, setInfo] = useState(initialState);

  return (
//ColorProvider에 state를 사용할 컴포넌트들을 호출하려면
//{children}이 있어야 합니다
//그래서 마지막 return에서 {children}을 리턴해줍니다.
    <UserContext.Provider value={info}>
      {children}
  	</UserContext.Provider>
  );
};

