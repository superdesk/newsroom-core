import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {get} from 'lodash';
import classNames from 'classnames';
import {fetchCompanyUsers} from 'assets/companies/actions';
import {canUserEditTopic} from 'assets/topics/utils';
import {globalTopicsEnabledSelector} from 'assets/ui/selectors';
import {fetchTopics, shareTopic, deleteTopic, selectMenuItem} from 'assets/user-profile/actions';
import {selectedItemSelector, selectedMenuSelector, topicEditorFullscreenSelector} from 'assets/user-profile/selectors';
import {canUserManageTopics} from 'assets/users/utils';
import {gettext, isActionEnabled} from 'assets/utils';
import types from 'fetch-mock';
import MonitoringEditor from './MonitoringEditor';
import TopicEditor from './TopicEditor';
import TopicList from './TopicList';

class FollowedTopics extends React.Component<any, any> {
    actions: Array<any>;
    static propTypes: any;

    constructor(props: any, context: any) {
        super(props, context);

        this.editTopic = this.editTopic.bind(this);
        this.deleteTopic = this.deleteTopic.bind(this);
        this.closeEditor = this.closeEditor.bind(this);
        this.getFilteredTopics = this.getFilteredTopics.bind(this);
        this.onTopicChanged = this.onTopicChanged.bind(this);
        this.toggleGlobal = this.toggleGlobal.bind(this);

        this.state = {showGlobal: false};

        this.actions = [{
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
                    when: (topic: any) => canUserEditTopic(topic, this.props.user),
                }
            ].filter(isActionEnabled('topic_actions'));
        }
    }

    componentDidMount() {
        this.onTopicChanged();
        if (this.props.user && this.props.user.company && this.props.user.company.length) {
            this.props.fetchCompanyUsers(this.props.user.company);
        }
    }

    componentDidUpdate(prevProps: any) {
        if (get(prevProps, 'selectedMenu') !== get(this.props, 'selectedMenu')) {
            this.closeEditor();
        }
    }

    componentWillUnmount() {
        this.closeEditor();
    }

    editTopic(topic: any) {
        this.props.selectMenuItem(topic);
    }

    deleteTopic(topic: any) {
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
            (topic: any) => (
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
        this.setState((previousState: any) => ({showGlobal: !previousState.showGlobal}));
    }

    render() {
        const editorOpen = this.props.selectedItem;
        const editorOpenInFullscreen = editorOpen && this.props.editorFullscreen;
        const containerClasses = classNames(
            'profile-content profile-content__topics container-fluid pe-0',
            {'ps-0': editorOpenInFullscreen}
        );

        return (
            <div className={containerClasses}>
                {!editorOpenInFullscreen && (
                    <div className="d-flex flex-column flex-grow-1">
                        {!this.props.globalTopicsEnabled ? null : (
                            <div className="pt-xl-4 pt-3 px-xl-4 me-0">
                                <div className="btn-group btn-group--navbar ms-0 me-3">
                                    <button
                                        className={classNames(
                                            'btn btn-outline-primary',
                                            {active: !this.state.showGlobal}
                                        )}
                                        onClick={this.toggleGlobal}
                                    >
                                        {gettext('My Topics')}
                                    </button>
                                    <button
                                        className={classNames(
                                            'btn btn-outline-primary',
                                            {active: this.state.showGlobal}
                                        )}
                                        onClick={this.toggleGlobal}
                                    >
                                        {gettext('Company Topics')}
                                    </button>
                                </div>
                            </div>
                        )}
                        <div className="row pt-xl-4 pt-3 px-xl-4 me-0">
                            <TopicList
                                topics={this.getFilteredTopics()}
                                selectedTopicId={get(this.props.selectedItem, '_id')}
                                actions={this.actions}
                                users={this.props.companyUsers}
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
};

const mapStateToProps = (state: any, ownProps: any) => ({
    topics: state.topics,
    monitoringList: state.monitoringList,
    monitoringAdministrator: state.monitoringAdministrator,
    user: state.user,
    selectedItem: selectedItemSelector(state),
    selectedMenu: selectedMenuSelector(state),
    editorFullscreen: topicEditorFullscreenSelector(state),
    globalTopicsEnabled: globalTopicsEnabledSelector(state, ownProps.topicType ),
    companyUsers: state.monitoringProfileUsers || []
});

const mapDispatchToProps = (dispatch: any) => ({
    fetchTopics: () => dispatch(fetchTopics()),
    shareTopic: (topic: any) => dispatch(shareTopic(topic)),
    deleteTopic: (topic: any) => dispatch(deleteTopic(topic)),
    selectMenuItem: (item: any) => dispatch(selectMenuItem(item)),
    fetchCompanyUsers: (companyId: any) => dispatch(fetchCompanyUsers(companyId, true)),
});

export default connect(mapStateToProps, mapDispatchToProps)(FollowedTopics);
