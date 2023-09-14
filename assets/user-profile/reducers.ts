import {
    GET_TOPICS,
    INIT_DATA,
    SET_ERROR,
    GET_USER,
    EDIT_USER,
    SELECT_MENU, HIDE_MODAL, TOGGLE_DROPDOWN,
    SELECT_MENU_ITEM,
    SELECT_PROFILE_MENU,
    SET_TOPIC_EDITOR_FULLSCREEN,
    RECIEVE_FOLDERS,
    TOPIC_UPDATED,
    FOLDER_UPDATED,
    FOLDER_DELETED,
} from './actions';

import {RENDER_MODAL, CLOSE_MODAL, MODAL_FORM_VALID, MODAL_FORM_INVALID, ADD_EDIT_USERS} from 'actions';
import {GET_COMPANY_USERS} from 'companies/actions';
import {SET_USER_COMPANY_MONITORING_LIST} from 'monitoring/actions';

import {modalReducer} from 'reducers';
import {GET_NAVIGATIONS, QUERY_NAVIGATIONS} from 'navigations/actions';
import {SET_TOPICS} from '../search/actions';
import {ITopicFolder} from 'interfaces';

export interface IUserProfileStore {
    allSections?: Array<any>;
    companySections?: any;
    seats?: any;
}

const initialState: any = {
    user: null,
    editedUser: null,
    company: null,
    topics: null,
    topicsById: {},
    activeTopicId: null,
    isLoading: false,
    selectedMenu: 'profile',
    dropdown: false,
    displayModal: false,
    navigations: [],
    selectedItem: null,
    editorFullscreen: false,
    locators: [],
    companyFolders: [],
    userFolders: [],
};

export default function itemReducer(state: any = initialState, action: any): IUserProfileStore {
    let newSelected, newState;
    switch (action.type) {

    case GET_TOPICS: {
        const topicsById = Object.assign({}, state.topicsById);
        const topics = action.topics.map((topic: any) => {
            topicsById[topic._id] = topic;
            return topic;
        });

        return {
            ...state,
            topics,
            topicsById,
            activeTopicId: null,
            isLoading: false
        };
    }

    case SET_TOPICS:
        return {
            ...state,
            topics: action.topics,
        };

    case GET_USER: {
        return {
            ...state,
            user: action.user,
            editedUser: action.user,
        };
    }

    case QUERY_NAVIGATIONS: {
        return {
            ...state,
            isLoading: true,
        };
    }

    case GET_NAVIGATIONS: {
        return {
            ...state,
            navigations: action.data,
            isLoading: false,
        };
    }

    case EDIT_USER: {

        const target = action.event.target;
        const field = target.name;
        const editedUser = Object.assign({}, state.editedUser);
        editedUser[field] = target.type === 'checkbox' ? target.checked : target.value;
        return {...state, editedUser, errors: null};
    }

    case INIT_DATA: {
        return {
            ...state,
            user: action.data.user || null,
            editedUser: action.data.user || null,
            topics: action.data.topics || [],
            company: action.data.company || null,
            userSections: action.data.userSections || null,
            locators: action.data.locators || null,
            monitoringList: action.data.monitoring_list || [],
            monitoringAdministrator: action.data.monitoring_administrator,
            uiConfigs: action.data.ui_configs,
            groups: action.data.groups || [],
        };
    }

    case SELECT_MENU: {
        return {
            ...state,
            selectedMenu: action.data,
            dropdown: false,
            displayModal: true,
        };
    }

    case SELECT_MENU_ITEM: {
        return {
            ...state,
            selectedItem: action.item,
            editorFullscreen: false,
        };
    }

    case SELECT_PROFILE_MENU: {
        return {
            ...state,
            selectedMenu: action.menu,
            selectedItem: action.item || state.selectedItem,
        };
    }

    case TOGGLE_DROPDOWN : {
        return {
            ...state,
            dropdown: !state.dropdown,
        };
    }

    case HIDE_MODAL: {
        return {
            ...state,
            displayModal: false,
        };
    }

    case RENDER_MODAL:
    case CLOSE_MODAL:
    case MODAL_FORM_VALID:
    case MODAL_FORM_INVALID:
        return {...state, modal: modalReducer(state.modal, action)};

    case SET_ERROR:
        return {...state, errors: action.errors};

    case SET_TOPIC_EDITOR_FULLSCREEN:
        return {
            ...state,
            editorFullscreen: action.payload,
        };

    case GET_COMPANY_USERS:
        return {...state, monitoringProfileUsers: action.data};

    case SET_USER_COMPANY_MONITORING_LIST:
        newSelected = state.selectedItem && (action.data || []).find((w: any) => w._id === state.selectedItem._id);
        newState = {
            ...state,
            monitoringList: action.data,

        };

        if (newSelected) {
            newState.selectedItem = newSelected;
        }

        return newState;

    case ADD_EDIT_USERS: {
        return {
            ...state,
            editUsers: [
                ...(state.editUsers || []),
                ...action.data,
            ]
        };
    }

    case RECIEVE_FOLDERS:
        return {
            ...state,
            companyFolders: action.payload.companyFolders,
            userFolders: action.payload.userFolders,
        };

    case TOPIC_UPDATED:
        return {
            ...state,
            topics: state.topics.map((topic: any) => {
                if (topic._id !== action.payload.topic._id) {
                    return topic;
                }

                return {...topic, ...action.payload.updates};
            }),
            selectedItem: state.selectedItem?._id === action.payload.topic._id ? {...state.selectedItem, ...action.payload.updates} : state.selectedItem,
        };

    case FOLDER_UPDATED: {
        const foldersToAccess = state.companyFolders.find(({_id}: ITopicFolder) => action.payload.folder._id === _id) != null
            ? 'companyFolders'
            : 'userFolders';

        return {
            ...state,
            [foldersToAccess]: state[foldersToAccess].map((folder: ITopicFolder) => {
                if (folder._id !== action.payload.folder._id) {
                    return folder;
                }

                return {...folder, ...action.payload.updates};
            }),
        };
    }

    case FOLDER_DELETED: {
        const foldersToAccess = state.companyFolders.find(({_id}: ITopicFolder) => action.payload.folder._id === _id) != null
            ? 'companyFolders'
            : 'userFolders';

        return {
            ...state,
            [foldersToAccess]: state[foldersToAccess].filter((folder: any) => folder._id !== action.payload.folder._id),
        };
    }

    default:
        return state;
    }
}
