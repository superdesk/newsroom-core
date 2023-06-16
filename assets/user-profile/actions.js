import {gettext, notify, errorHandler} from 'utils';
import server from 'server';
import {renderModal, closeModal} from 'actions';
import {store as userProfileStore} from './store';
import {getLocale} from '../utils';
import {reloadMyTopics as reloadMyAgendaTopics} from '../agenda/actions';
import {reloadMyTopics as reloadMyWireTopics} from '../wire/actions';

export const GET_TOPICS = 'GET_TOPICS';
export function getTopics(topics) {
    return {type: GET_TOPICS, topics};
}

export const GET_USER = 'GET_USER';
export function getUser(user) {
    return {type: GET_USER, user};
}

export const EDIT_USER = 'EDIT_USER';
export function editUser(event) {
    return {type: EDIT_USER, event};
}

export const INIT_DATA = 'INIT_DATA';
export function initData(data) {
    return {type: INIT_DATA, data};
}

export const SET_ERROR = 'SET_ERROR';
export function setError(errors) {
    return {type: SET_ERROR, errors};
}

export const SELECT_MENU = 'SELECT_MENU';
export function selectMenu(data) {
    return function(dispatch) {
        dispatch({type: SELECT_MENU, data});
        dispatch(reloadMyTopics());
    };
}

export const SET_TOPIC_EDITOR_FULLSCREEN = 'SET_TOPIC_EDITOR_FULLSCREEN';
export function setTopicEditorFullscreen(fullscreen) {
    return {type: SET_TOPIC_EDITOR_FULLSCREEN, payload: fullscreen};
}

export const SELECT_MENU_ITEM = 'SELECT_MENU_ITEM';
export function selectMenuItem(item) {
    return {type: SELECT_MENU_ITEM, item};
}

export function createOrUpdateTopic(menu, item, fullscreen) {
    userProfileStore.dispatch(selectMenuItem(item));
    userProfileStore.dispatch(selectMenu(menu));
    userProfileStore.dispatch(setTopicEditorFullscreen(fullscreen));
}

export const SELECT_PROFILE_MENU = 'SELECT_PROFILE_MENU';
export function selectProfileMenu({menu, item}) {
    userProfileStore.dispatch({
        type: SELECT_PROFILE_MENU,
        menu: menu,
        item: item,
    });
}

export const TOGGLE_DROPDOWN = 'TOGGLE_DROPDOWN';
export function toggleDropdown() {
    return {type: TOGGLE_DROPDOWN};
}

export const HIDE_MODAL = 'HIDE_MODAL';
export function hideModal() {
    return {type: HIDE_MODAL};
}


/**
 * Fetches user details
 */
export function fetchUser(id) {
    return function (dispatch) {
        return server.get(`/users/${id}`)
            .then((data) => {
                dispatch(getUser(data));
            })
            .catch((error) => errorHandler(error, dispatch, setError));
    };
}

/**
 * Saves a user
 *
 */
export function saveUser() {
    return function (dispatch, getState) {

        const editedUser = {...getState().editedUser};
        const url = `/users/${editedUser._id}/profile`;

        // Remove ``sections`` and ``products`` as these aren't managed in the ``UserProfile`` app
        delete editedUser.sections;
        delete editedUser.products;

        return server.post(url, editedUser)
            .then(function() {
                notify.success(gettext('User updated successfully'));
                dispatch(fetchUser(editedUser._id));
                if (editedUser.locale && getLocale() !== editedUser.locale) {
                    notify.warning(
                        gettext(
                            'Please reload the page in order to change language.'
                        )
                    );
                }
            })
            .catch((error) => errorHandler(error, dispatch, setError));

    };
}

/**
 * Fetches followed topics for the user
 *
 */
export function fetchTopics() {
    return function (dispatch, getState) {
        return server.get(`/users/${getState().user._id}/topics`)
            .then((data) => {
                return dispatch(getTopics(data._items));
            })
            .catch((error) => errorHandler(error, dispatch, setError));
    };
}

/**
 * Deletes the given followed topic
 *
 */
export function deleteTopic(topic) {
    return function (dispatch) {
        const url = `/topics/${topic._id}`;
        return server.del(url)
            .then(() => {
                notify.success(gettext('Topic deleted successfully'));
                dispatch(fetchTopics());
            })
            .catch((error) => errorHandler(error, dispatch, setError));
    };
}

/**
 * Start share followed topic - display modal to pick users
 *
 * @return {function}
 */
export function shareTopic(items) {
    return (dispatch, getState) => {
        const user = getState().user;
        const company = getState().company;
        return server.get(`/companies/${company}/users`)
            .then((users) => users.filter((u) => u._id !== user._id))
            .then((users) => dispatch(renderModal('shareItem', {items, users})))
            .catch(errorHandler);
    };
}

/**
 * Submit share followed topic form and close modal if that works
 *
 * @param {Object} data
 */
export function submitShareTopic(data) {
    return (dispatch) => {
        return server.post('/topic_share', data)
            .then(() => {
                notify.success(gettext('Topic was shared successfully.'));
                dispatch(closeModal());
            })
            .catch(errorHandler);
    };
}


/**
 * Updates a followed topic
 *
 */
export function submitFollowTopic(topic) {
    return (dispatch) => {
        const url = `/topics/${topic._id}`;
        return server.post(url, topic)
            .then(() => dispatch(fetchTopics()))
            .then(() => dispatch(closeModal()))
            .catch(errorHandler);
    };
}

function reloadMyTopics() {
    return function(dispatch, getState) {
        const reloadMyTopicsFunction = getState().selectedMenu === 'events' ? reloadMyAgendaTopics : reloadMyWireTopics;

        return dispatch(reloadMyTopicsFunction());
    };
}

export function pushNotification(push) {
    return (dispatch, getState) => {
        const user = getState().user;
        const company = getState().company;
        const shouldReloadTopics = [
            `topics:${user}`,
            `topics:company-${company}`,
            `topic_created:${user}`,
            `topic_created:company-${company}`,
        ].includes(push.event);

        if (shouldReloadTopics) {
            return dispatch(reloadMyTopics());
        }
    };
}

function getUserFoldersUrl(state, id) {
    const baseUrl = `/api/users/${state.user._id}/topic_folders`;

    return id != null ? `${baseUrl}/${id}` : baseUrl;
}

function getFoldersUrl(state, global, id) {
    const baseUrl = global ?
        `/api/companies/${state.company}/topic_folders` :
        `/api/users/${state.user._id}/topic_folders`;

    return id != null ? `${baseUrl}/${id}` : baseUrl;
}

function mergeUpdates(updates, response) {
    updates._id = response._id;
    updates._etag = response._etag;
    updates._status = response._status;
    updates._updated = response._updated;
}

export const FOLDER_UPDATED = 'FOLDER_UPDATED';
export function saveFolder(folder, data, global) {
    return (dispatch, getState) => {
        const state = getState();
        const url = getFoldersUrl(state, global, folder._id);

        if (folder._etag) {
            const updates = {...data};

            return server.patch(url, updates, folder._etag)
                .then(() => {
                    dispatch(fetchFolders(global, true));
                });
        } else {
            const payload = {...data, section: state.selectedMenu === 'events' ? 'agenda' : 'wire'};

            return server.post(url, payload)
                .then(() => {
                    dispatch(fetchFolders(global));
                });
        }
    };
}

export const FOLDER_DELETED = 'FOLDER_DELETED';
export function deleteFolder(folder, deleteTopics) {
    return (dispatch, getState) => {
        const state = getState();
        const url = getUserFoldersUrl(state, folder._id);

        if (!window.confirm(gettext('Are you sure you want to delete folder?'))) {
            return;
        }

        return server.del(url, {topics: deleteTopics}, folder._etag)
            .then(() => dispatch({type: FOLDER_DELETED, payload: {folder}}));
    };
}

export const RECIEVE_FOLDERS = 'RECIEVE_FOLDERS';

export function fetchUserFolders() {
    return (dispatch, getState) => {
        const state = getState();
        const url = getUserFoldersUrl(state);

        return server.get(url).then((res) => {
            dispatch({type: RECIEVE_FOLDERS, payload: res._items});
        }, (reason) => {
            console.error(reason);
            return Promise.reject();
        });
    };
}

/**
 * @param {bool} global - fetch company or user folders
 * @param {bool} force  - force refresh via adding timestamp to url
 */
export function fetchFolders(global, force) {
    return (dispatch, getState) => {
        const state = getState();
        const url = getFoldersUrl(state, global) + (force ? `?time=${Date.now()}` : '');

        return server.get(url).then((res) => {
            dispatch({type: RECIEVE_FOLDERS, payload: res._items});
        }, (reason) => {
            console.error(reason);
            return Promise.reject();
        });
    };
}

export const TOPIC_UPDATED = 'TOPIC_UPDATED';
export function moveTopic(topicId, folder) {
    return (dispatch, getState) => {
        const updates = {
            folder: folder != null ? folder._id : null,
        };

        const state = getState();
        const topic = state.topics.find((topic) => topic._id === topicId);
        const url = `/api/users/${state.user._id}/topics/${topicId}`;

        server.patch(url, updates, topic._etag).then((response) => {
            mergeUpdates(updates, response);
            dispatch({type: TOPIC_UPDATED, payload: {topic, updates}});
        });
    };
}
