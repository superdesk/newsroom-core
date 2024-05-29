import {ICompany, ICountry, IProduct, ISearchState, ISection, IUser} from 'interfaces';

import {
    INIT_VIEW_DATA,
    GET_USERS,
    GET_USER,
    REMOVE_USER,
    SELECT_USER,
    EDIT_USER__DEPRECATED,
    QUERY_USERS,
    CANCEL_EDIT,
    NEW_USER,
    SET_ERROR,
    GET_COMPANIES,
    SET_COMPANY,
    SET_SORT,
    TOGGLE_SORT_DIRECTION,
    EDIT_USER,
} from './actions';

import {ADD_EDIT_USERS} from 'actions';

import {searchReducer} from 'search/reducers';

export interface IUserSettingsState {
    user?: IUser;
    users: IUser['_id'][];
    usersById: {[key: IUser['_id']]: IUser};
    totalUsers?: number;
    sortDirection: -1 | 1;
    activeQuery?: string;
    activeUserId?: string;
    editUsers?: IUser[];
    company?: ICompany['_id'];
    companies: ICompany[];
    companiesById: {[key: ICompany['_id']]: ICompany};
    query?: string;
    userToEdit?: Partial<IUser>;
    isLoading: boolean;
    sort?: string;
    search: ISearchState;
    sections: ISection[];
    products: IProduct[];
    countries: ICountry[];
    errors?: {[field: string]: string[]};
    authProviderFeatures: {
        [provider: string]: {
            verify_email: boolean;
            change_password: boolean;
        };
    };
}

const initialState: IUserSettingsState = {
    users: [],
    usersById: {},
    isLoading: false,
    companies: [],
    sortDirection: 1,
    search: searchReducer(undefined, undefined, 'settings'),
    sections: [],
    products: [],
    countries: [],
    companiesById: {},
    authProviderFeatures: {},
};

export default function userReducer(state: IUserSettingsState = initialState, action: any): IUserSettingsState {
    switch (action.type) {
    case INIT_VIEW_DATA:
        return {
            ...state,
            sections: action.data.sections,
            products: action.data.products,
            countries: action.data.countries,
            authProviderFeatures: action.data.auth_provider_features,
        };

    case SELECT_USER: {
        const defaultUser: any = {
            user_type: 'public',
            is_approved: true,
            is_enabled: true,
            first_name: '',
            last_name: '',
            email: '',
            phone: '',
            mobile: '',
            role: '',
            company: state.company,
        };

        return {
            ...state,
            activeUserId: action.id,
            userToEdit: action.id ? Object.assign(defaultUser, state.usersById[action.id]) : undefined,
            errors: undefined,
        };
    }

    case GET_USER: {
        return {
            ...state,
            user: action.user,
        };
    }

    case EDIT_USER__DEPRECATED: {
        const target = action.event.target;
        const field = target.name;
        const user: any = {...state.userToEdit};
        const value = target.type === 'checkbox' ? target.checked : target.value;

        if (action.event?.changeType === 'company') {
            if ((value || '').length > 0) {
                user.sections = {}; // Defaults to use `company.sections` for permissions
                user.company = value;
            } else {
                user.company = null;
            }
        } else if (field.startsWith('sections.')) {
            const sectionId = field.replace('sections.', '');
            const company = state.companies.find((company) => company._id === user.company);

            user.sections = {
                ...company?.sections || {},
                ...user.sections || {},
                [sectionId]: value,
            };
        } else if (field.startsWith('products.')) {
            const [section, productId] = field.replace('products.', '').split('.');

            if (value) {
                user.products = [
                    ...user.products || [],
                    {
                        _id: productId,
                        section: section,
                    },
                ];
            } else {
                user.products = (user.products || []).filter((product: any) => product._id !== productId);
            }
        }
        else {
            user[field] = value;
        }

        return {...state, userToEdit: user, errors: undefined};
    }

    case EDIT_USER:
        return {
            ...state,
            userToEdit: action.payload,
            errors: undefined,
        };

    case NEW_USER: {
        const newUser: Partial<IUser> = {
            user_type: 'public',
            is_approved: true,
            is_enabled: true,
            email: '',
            phone: '',
        };

        if (state.company) {
            newUser.company = state.company;
        }

        return {...state, userToEdit: newUser, errors: undefined};
    }

    case CANCEL_EDIT: {
        return {...state, userToEdit: undefined, errors: undefined};
    }

    case SET_ERROR:
        return {...state, errors: action.errors};

    case QUERY_USERS:
        return {...state,
            isLoading: true,
            totalUsers: undefined,
            userToEdit: undefined,
            activeQuery: state.query};

    case GET_USERS: {
        const usersById = Object.assign({}, state.usersById);
        const users = action.data.map((user: any) => {
            usersById[user._id] = user;
            return user._id;
        });

        return {
            ...state,
            users,
            usersById,
            isLoading: false,
            totalUsers: users.length,
        };
    }

    case REMOVE_USER: {
        const usersById = Object.assign({}, state.usersById);
        const userToEdit = state.userToEdit && state.userToEdit._id === action.userId ?
            undefined :
            state.userToEdit;
        const users = state.users.filter((userId: any) => userId !== action.userId);

        delete usersById[action.userId];

        return {
            ...state,
            usersById,
            userToEdit,
            users,
            errors: undefined,
        };
    }

    case GET_COMPANIES: {
        const companiesById: any = {};
        action.data.map((company: any) => companiesById[company._id] = company);

        return {...state, companies: action.data, companiesById};

    }

    case SET_COMPANY: {
        return {...state, company: action.company};
    }

    case SET_SORT: {
        return {
            ...state,
            sort: action.param,
            sortDirection: 1
        };
    }

    case TOGGLE_SORT_DIRECTION: {
        return {...state, sortDirection: state.sortDirection === 1 ? -1 : 1};
    }

    case ADD_EDIT_USERS: {
        return {
            ...state,
            editUsers: [
                ...(state.editUsers || []),
                ...action.data,
            ]
        };
    }

    default: {
        const search = searchReducer(state.search, action, 'settings');

        if (search !== state.search) {
            return {...state, search};
        }

        return state;
    }
    }
}
