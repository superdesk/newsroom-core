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

import {RENDER_MODAL, CLOSE_MODAL, MODAL_FORM_VALID, MODAL_FORM_INVALID} from 'actions';

import {IModalState, modalReducer} from 'reducers';
import {GET_NAVIGATIONS, QUERY_NAVIGATIONS} from 'navigations/actions';
import {SET_TOPICS} from '../search/actions';
import {ISection, ITopic, ITopicFolder, IUser} from 'interfaces';

export interface IUserProfileState {
    user: IUser | null;
    editedUser: Partial<IUser> | null;
    company: string | null;
    topics: ITopic[];
    topicsById: {[_id: ITopic['_id']]: ITopic};
    activeTopicId: ITopic['_id'] | null;
    isLoading: boolean;
    selectedMenu: 'profile' | 'topics' | 'events' | 'monitoring';
    dropdown: boolean;
    displayModal: boolean;
    navigations: [];
    selectedItem: ITopic | null;
    editorFullscreen: boolean;
    locators: [];
    companyFolders: ITopicFolder[];
    userFolders: ITopicFolder[];
    authProviderFeatures?: {
        change_password: boolean;
        verify_password: boolean;
    };
    errors: {[key: string]: string[]} | null;
    modal?: IModalState;
    userSections?: ISection[];
    monitoringList?: Array<any>;
    monitoringAdministrator?: string;
    uiConfigs?: any;
    groups?: Array<any>;
}

const initialState: IUserProfileState = {
    user: null,
    editedUser: null,
    company: null,
    topics: [],
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
    errors: {},
};

export default function itemReducer(state: IUserProfileState = initialState, action: any): IUserProfileState {
    switch (action.type) {

    case GET_TOPICS: {
        const topicsById = Object.assign({}, state.topicsById);
        const topics = action.topics.map((topic: ITopic) => {
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
        const editedUser = Object.assign({}, state.editedUser, action.payload);
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
            authProviderFeatures: {
                verify_password: action.data.authProviderFeatures?.verify_password === true,
                change_password: action.data.authProviderFeatures?.change_password === true,
            },
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
