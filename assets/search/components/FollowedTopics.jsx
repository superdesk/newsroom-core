import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {get} from 'lodash';
import classNames from 'classnames';

import types from 'wire/types';
import {gettext, isActionEnabled} from 'utils';
import {canUserManageTopics} from 'users/utils';
import {canUserEditTopic} from 'topics/utils';
import {fetchCompanyUsers} from 'companies/actions';

import {
    fetchTopics,
    shareTopic,
    deleteTopic,
    selectMenuItem,
    saveFolder,
    deleteFolder,
    fetchFolders,
    moveTopic,
} from 'user-profile/actions';

import {
    selectedItemSelector,
    selectedMenuSelector,
    topicEditorFullscreenSelector,
    globalTopicsEnabledSelector,
    foldersSelector,
} from 'user-profile/selectors';

import MonitoringEditor from 'search/components/MonitoringEditor';
import TopicEditor from 'search/components/TopicEditor';
import TopicList from 'search/components/TopicList';
import {TopicFolderEditor} from './TopicFolderEditor';

class FollowedTopics extends React.Component {
    constructor(props, context) {
        super(props, context);

        this.editTopic = this.editTopic.bind(this);
        this.deleteTopic = this.deleteTopic.bind(this);
        this.closeEditor = this.closeEditor.bind(this);
        this.getFilteredTopics = this.getFilteredTopics.bind(this);
        this.onTopicChanged = this.onTopicChanged.bind(this);
        this.toggleGlobal = this.toggleGlobal.bind(this);
        this.toggleFolderPopover = this.toggleFolderPopover.bind(this);
        this.saveFolder = this.saveFolder.bind(this);
        this.removeTopicFolder = this.removeTopicFolder.bind(this);

        this.state = {showGlobal: false, newFolder: null, folderPopover: null};

        this.actions = [
            {
                id: 'move',
                name: gettext('Remove from folder'),
                icon: 'folder-remove-from',
                action: this.removeTopicFolder,
                if: (topic) => topic.folder != null,
            },
            {
                id: 'edit',
                name: gettext('Edit'),
                icon: 'edit',
                action: this.editTopic,
            }];

        if (this.props.topicType !== 'monitoring') {
            this.actions = [
                ...this.actions,
                {
                    id: 'share',
                    name: gettext('Share'),
                    icon: 'share',
                    action: this.props.shareTopic,
                }, {
                    id: 'delete',
                    name: gettext('Delete'),
                    icon: 'trash',
                    action: this.deleteTopic,
                    when: (topic) => canUserEditTopic(topic, this.props.user),
                }
            ].filter(isActionEnabled('topic_actions'));
        }
    }

    componentDidMount() {
        this.onTopicChanged();
        if (this.props.user && this.props.user.company && this.props.user.company.length) {
            this.props.fetchCompanyUsers(this.props.user.company);
        }

        if (this.props.user) {
            this.props.fetchFolders();
        }
    }

    componentDidUpdate(prevProps) {
        if (get(prevProps, 'selectedMenu') !== get(this.props, 'selectedMenu')) {
            this.closeEditor();
        }
    }

    componentWillUnmount() {
        this.closeEditor();
    }

    editTopic(topic) {
        this.props.selectMenuItem(topic);
    }

    deleteTopic(topic) {
        confirm(
            gettext('Would you like to delete topic {{name}}?', {
                name: topic.label,
            })
        ) && this.props.deleteTopic(topic);
    }

    closeEditor() {
        this.props.selectMenuItem(null);
    }

    getFilteredTopics() {
        if (this.props.topicType === 'monitoring') {
            return this.props.monitoringList;
        }

        return this.props.topics.filter(
            (topic) => (
                topic.topic_type === this.props.topicType &&
                (topic.is_global || false) === this.state.showGlobal
            )
        );
    }

    onTopicChanged() {
        this.props.fetchTopics();
    }

    isMonitoringAdmin() {
        return this.props.monitoringAdministrator === get(this.props, 'user._id');
    }

    toggleGlobal() {
        this.setState((previousState) => ({showGlobal: !previousState.showGlobal}));
        this.props.fetchFolders(!this.state.showGlobal); // state change will only happen later
    }

    createNewFolder() {
        this.setState({newFolder: {}, folderPopover: null});
    }

    saveFolder(folder, changes) {
        this.props.saveFolder(folder, changes, this.state.showGlobal).then(() => {
            this.setState({newFolder: null, folderPopover: null});
        }, (reason) => {
            this.setState({newFolder: {error: reason}});
        });
    }

    toggleFolderPopover(folder) {
        this.setState({folderPopover: !this.state.folderPopover || this.state.folderPopover !== folder._id ? folder._id : null});
    }

    removeTopicFolder(topic) {
        this.props.moveTopic(topic._id);
    }

    render() {
        const editorOpen = this.props.selectedItem;
        const editorOpenInFullscreen = editorOpen && this.props.editorFullscreen;
        const containerClasses = classNames(
            'profile-content profile-content--topics',
            {'ps-0': editorOpenInFullscreen}
        );

        return (
            <div className={containerClasses}>
                {!editorOpenInFullscreen && (
                    <div className="profile-content__main d-flex flex-column flex-grow-1">
                        <div className="d-flex justify-content-between pt-xl-4 pt-3">
                            {!this.props.globalTopicsEnabled ? null : (
                                <div className="toggle-button__group toggle-button__group--navbar ms-0 me-3">
                                    <button
                                        className={classNames(
                                            'toggle-button',
                                            {'toggle-button--active': !this.state.showGlobal}
                                        )}
                                        onClick={this.toggleGlobal}
                                    >
                                        {gettext('My Topics')}
                                    </button>
                                    <button
                                        className={classNames(
                                            'toggle-button',
                                            {'toggle-button--active': this.state.showGlobal}
                                        )}
                                        onClick={this.toggleGlobal}
                                    >
                                        {gettext('Company Topics')}
                                    </button>
                                </div>
                            )}
                            <div className="toggle-button__group toggle-button__group--navbar ms-0 me-0">
                                <button type="button" className="nh-button nh-button--tertiary"
                                    title={gettext('Create new folder')}
                                    onClick={() => this.createNewFolder()}>
                                    <i className="icon--folder-create"></i>{gettext('New folder')}
                                </button>
                            </div>
                        </div>
                        <div className="simple-card__list pt-xl-4 pt-3">
                            {this.state.newFolder != null && (
                                <div className="simple-card__group">
                                    <TopicFolderEditor
                                        folder={this.state.newFolder}
                                        error={this.state.newFolder.error}
                                        onSave={(name) => this.saveFolder(this.state.newFolder, {name})}
                                        onCancel={() => this.setState({newFolder: null})}
                                    />
                                </div>
                            )}
                            <TopicList
                                topics={this.getFilteredTopics()}
                                selectedTopicId={get(this.props.selectedItem, '_id')}
                                actions={this.actions}
                                users={this.props.companyUsers}
                                folders={this.props.folders}
                                folderPopover={this.state.folderPopover}
                                toggleFolderPopover={this.toggleFolderPopover}
                                moveTopic={this.props.moveTopic}
                                saveFolder={this.props.saveFolder}
                                deleteFolder={this.props.deleteFolder}
                            />
                        </div>
                    </div>
                )}
                {this.props.selectedItem && (this.props.topicType === 'monitoring' ?
                    <MonitoringEditor
                        item={this.props.selectedItem}
                        closeEditor={this.closeEditor}
                        onTopicChanged={this.onTopicChanged}
                        isAdmin={this.isMonitoringAdmin()}
                    /> :
                    <TopicEditor
                        topic={this.props.selectedItem}
                        globalTopicsEnabled={this.props.globalTopicsEnabled}
                        closeEditor={this.closeEditor}
                        onTopicChanged={this.onTopicChanged}
                        isAdmin={canUserManageTopics(this.props.user)}
                        user={this.props.user}
                        companyUsers={this.props.companyUsers}
                    />)}
            </div>
        );
    }
}

FollowedTopics.propTypes = {
    fetchTopics: PropTypes.func.isRequired,
    topics: types.topics,
    topicType: PropTypes.string.isRequired,
    shareTopic: PropTypes.func,
    deleteTopic: PropTypes.func,
    selectMenuItem: PropTypes.func,
    selectedItem: types.topic,
    selectedMenu: PropTypes.string,
    editorFullscreen: PropTypes.bool,
    monitoringList: PropTypes.array,
    monitoringAdministrator: PropTypes.string,
    globalTopicsEnabled: PropTypes.bool,
    user: PropTypes.object,
    fetchCompanyUsers: PropTypes.func,
    companyUsers: PropTypes.array,
    fetchFolders: PropTypes.func,
    moveTopic: PropTypes.func,
    saveFolder: PropTypes.func,
    deleteFolder: PropTypes.func,
    folders: PropTypes.arrayOf(PropTypes.shape({
        name: PropTypes.string.isRequired,
        section: PropTypes.string.isRequired,
    })),
};

const mapStateToProps = (state, ownProps) => ({
    topics: state.topics,
    monitoringList: state.monitoringList,
    monitoringAdministrator: state.monitoringAdministrator,
    user: state.user,
    selectedItem: selectedItemSelector(state),
    selectedMenu: selectedMenuSelector(state),
    editorFullscreen: topicEditorFullscreenSelector(state),
    globalTopicsEnabled: globalTopicsEnabledSelector(state, ownProps.topicType),
    companyUsers: state.monitoringProfileUsers || [],
    folders: foldersSelector(state),
});

const mapDispatchToProps = (dispatch) => ({
    fetchTopics: () => dispatch(fetchTopics()),
    shareTopic: (topic) => dispatch(shareTopic(topic)),
    deleteTopic: (topic) => dispatch(deleteTopic(topic)),
    selectMenuItem: (item) => dispatch(selectMenuItem(item)),
    fetchCompanyUsers: (companyId) => dispatch(fetchCompanyUsers(companyId, true)),
    saveFolder: (folder, data, global) => dispatch(saveFolder(folder, data, global)),
    fetchFolders: (global) => dispatch(fetchFolders(global)),
    moveTopic: (topicId, folder) => dispatch(moveTopic(topicId, folder)),
    deleteFolder: (folder) => dispatch(deleteFolder(folder)),
});

export default connect(mapStateToProps, mapDispatchToProps)(FollowedTopics);
