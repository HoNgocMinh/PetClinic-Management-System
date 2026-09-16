import cookie from 'react-cookies';

const MyUserReducer = (currentState, action) => {
    switch (action.type) {
        case "login":
            return action.payload;
        case "logout":
            cookie.remove('token', { path: '/' });
            cookie.remove('user', { path: '/' });
            return null;
        default:
            return currentState;
    }
}

export default MyUserReducer;