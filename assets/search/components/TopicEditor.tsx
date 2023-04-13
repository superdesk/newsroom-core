import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {get, set, cloneDeep, isEqual} from 'lodash';
import classNames from 'classnames';
import {loadMyAgendaTopic} from 'assets/agenda/actions';
import AuditInformation from 'assets/components/AuditInformation';
import EditPanel from 'assets/components/EditPanel';
import {fetchNavigations} from 'assets/navigations/actions';
import {canUserEditTopic} from 'assets/topics/utils';
import {ToolTip} from 'assets/ui/components/ToolTip';
import {hideModal, setTopicEditorFullscreen} from 'assets/user-profile/actions';
import {topicEditorFullscreenSelector} from 'assets/user-profile/selectors';
import {gettext, notify} from 'assets/utils';
import {loadMyWireTopic} from 'assets/wire/actions';
import types from 'fetch-mock';
import {unsubscribeToTopic, subscribeToTopic} from '../actions';
import TopicForm from './TopicForm';
import TopicParameters from './TopicParameters';

class TopicEditor extends React.Component<any, any> {
    static propTypes: any;
    constructor(props: any) {
        super(props);

        this.state = {
            topic: null,
            saving: false,
            valid: false,
            tabs: [],
            activeTab: 'topic',
        };

        this.onChangeHandler = this.onChangeHandler.bind(this);
        this.onSubscribeChanged = this.onSubscribeChanged.bind(this);
        this.saveTopic = this.saveTopic.bind(this);
        this.handleTabClick = this.handleTabClick.bind(this);
    }

    componentDidMount() {
        this.props.fetchNavigations();

        if (this.props.topic != null) {
            this.changeTopic(this.props.topic);
        }
    }

    componentDidUpdate(prevProps: any) {
        if (get(prevProps, 'topic._id') !== get(this.props, 'topic._id')) {
            this.changeTopic(this.props.topic);
        }
    }

    handleTabClick(event: any) {
        this.setState({activeTab: event.target.name});
    }

    changeTopic(topic: any) {
        topic.notifications = (topic.subscribers || []).includes(this.props.userId);

        this.setState({
            topic: topic,
            saving: false,
            valid: !get(topic, '_id'),
            tabs:  this.getTabsForTopic(topic),
            activeTab: 'topic',
        }, () => {
            this.updateFormValidity(topic);
        });
    }

    getTabsForTopic(topic: any) {
        return (!topic._id || !topic.is_global || !this.props.isAdmin) ?
            [] :
            [
                {label: gettext('Company Topic'), name: 'topic', tooltip: gettext('Edit Metadata')},
                {label: gettext('Subscribers'), name: 'subscribers', tooltip: gettext('Email Notifications')},
            ];
    }

    updateFormValidity(topic: any) {
        const original = get(this.props, 'topic') || {};
        const isDirty = ['label', 'notifications', 'is_global'].some(
            (field) => get(original, field) !== get(topic, field)
        ) || !isEqual(original.subscribers, topic.subscribers);

        if (!topic.label) {
            // The topic must have a label so disable the save button
            this.setState({valid: false});
        } else if (isDirty) {
            // If the label or notification have changed, then enable the save button
            this.setState({valid: true});
        } else if (original._id) {
            // Otherwise the form is not dirty
            // Set the valid flag to true if in fullscreen
            this.setState({valid: this.props.editorFullscreen});
        }
    }

    onChangeHandler(field: any) {
        return (event: any) => {
            const topic = cloneDeep(this.state.topic);
            const value = ['notifications', 'is_global'].includes(field) ?
                !get(topic, field) :
                event.target.value;

            set(topic, field, value);
            this.setState({topic});
            this.updateFormValidity(topic);
        };
    }

    onSubscribeChanged() {
        const topic = cloneDeep(this.state.topic);

        if (this.state.topic.notifications) {
            unsubscribeToTopic(this.state.topic);
            topic.notifications = false;
            topic.subscribers = (topic.subscribers || []).filter((userId: any) => userId !== this.props.userId);
        } else {
            subscribeToTopic(this.state.topic);
            topic.notifications = true;
            topic.subscribers = [
                ...(topic.subscribers || []),
                this.props.userId
            ];
        }

        this.setState({topic});
        this.props.onTopicChanged();
    }

    saveTopic(event: any) {
        const original = this.props.topic;
        const topic = cloneDeep(this.state.topic);
        const isExisting = !this.isNewTopic();
        const isAgendaTopic = this.isAgendaTopic();

        // Construct new list of subscribers
        if (!isExisting || !original.is_global) {
            let subscribers = topic.subscribers || [];
            const alreadySubscribed = subscribers.includes(this.props.userId);

            if (topic.notifications && !alreadySubscribed) {
                subscribers.push(this.props.userId);
            } else if (!topic.notifications && alreadySubscribed) {
                subscribers = subscribers.filter(
                    (userId: any) => userId !== this.props.userId
                );
            }

            delete topic.notifications;
            topic.subscribers = subscribers || [];
        }

        event.preventDefault && event.preventDefault();
        this.setState({saving: true});
        this.props.saveTopic(
            isExisting,
            topic
        )
            .then((savedTopic: any) => {
                this.setState({saving: false});
                this.props.onTopicChanged();
                this.props.closeEditor();

                if (isExisting) {
                    notify.success(isAgendaTopic ?
                        gettext('Agenda Topic updated successfully') :
                        gettext('Wire Topic updated successfully')
                    );
                } else {
                    notify.success(isAgendaTopic ?
                        gettext('Agenda Topic created successfully') :
                        gettext('Wire Topic created successfully')
                    );

                    this.props.loadMyTopic(savedTopic);
                }

                if (this.props.editorFullscreen) {
                    this.props.hideModal();
                    this.props.setTopicEditorFullscreen(false);
                }
            });
    }

    isNewTopic() {
        return !get(this.state, 'topic._id');
    }

    isAgendaTopic() {
        return get(this.state, 'topic.topic_type') === 'agenda';
    }

    getTitle() {
        if (this.isNewTopic()) {
            return this.isAgendaTopic() ?
                gettext('Create new Agenda Topic') :
                gettext('Create new Wire Topic');
        } else {
            return this.isAgendaTopic() ?
                gettext('Save Agenda Topic') :
                gettext('Save Wire Topic');
        }
    }

    render() {
        // Wait for navigations to be loaded
        if (this.props.isLoading) {
            return null;
        }

        const originalTopic = this.props.topic || {};
        const updatedTopic = this.state.topic || {};
        const currentUser = this.props.user || {};

        const isCompanyTopic = originalTopic.is_global;
        const isReadOnly = !canUserEditTopic(originalTopic, currentUser);
        const showTabs = this.state.tabs.length > 0;

        const containerClasses = classNames(
            'list-item__preview',
            {'list-item__preview--new': this.props.editorFullscreen}
        );

        return (
            <div className={showTabs ? 'list-item__preview' : containerClasses}>
                <div className="list-item__preview-header">
                    <h3>{this.getTitle()}</h3>
                    <button
                        id="hide-sidebar"
                        type="button"
                        className="icon-button"
                        onClick={this.props.closeEditor}
                        disabled={this.state.saving}
                        aria-label={gettext('Close')}
                    >
                        <i className="icon--close-thin icon--gray-dark" />
                    </button>
                </div>
                {!isCompanyTopic ? null : (
                    <AuditInformation
                        item={originalTopic}
                        users={this.props.companyUsers}
                    />
                )}
                {!showTabs ? null : (
                    <ul className='nav nav-tabs'>
                        {this.state.tabs.map((tab: any) => (
                            <li
                                key={tab.name}
                                className='nav-item'
                            >
                                <ToolTip placement="bottom">
                                    <a
                                        name={tab.name}
                                        className={`nav-link ${this.state.activeTab === tab.name && 'active'}`}
                                        href='#'
                                        title={tab.tooltip}
                                        onClick={this.handleTabClick}>{tab.label}
                                    </a>
                                </ToolTip>
                            </li>
                        ))}
                    </ul>
                )}
                <div className={classNames(
                    'list-item__preview-form',
                    {'list-item__preview-form--no-padding': this.state.activeTab === 'subscribers'}
                )}>
                    {this.state.activeTab === 'topic' && updatedTopic && (
                        <React.Fragment>
                            <TopicForm
                                original={originalTopic}
                                globalTopicsEnabled={this.props.globalTopicsEnabled}
                                topic={updatedTopic}
                                save={this.saveTopic}
                                onChange={this.onChangeHandler}
                                onSubscribeChanged={this.onSubscribeChanged}
                                readOnly={isReadOnly}
                            />
                            <TopicParameters
                                topic={updatedTopic}
                                navigations={this.props.navigations}
                            />
                        </React.Fragment>
                    )}
                    {this.state.activeTab === 'subscribers' && updatedTopic && (
                        <EditPanel
                            parent={updatedTopic}
                            items={this.props.companyUsers.map((user: any) => ({
                                ...user,
                                name: `${user.first_name} ${user.last_name}`,
                            }))}
                            field="subscribers"
                            onChange={this.onChangeHandler('subscribers')}
                            onSave={this.saveTopic}
                            onCancel={this.props.closeEditor}
                            saveDisabled={this.state.saving || !this.state.valid}
                            cancelDisabled={this.state.saving}
                            includeSelectAll={true}
                            title={gettext('Send notifications to:')}
                        />
                    )}
                </div>
                {(this.state.activeTab === 'subscribers' || isReadOnly) ? null : (
                    <div className="list-item__preview-footer">
                        <input
                            type="button"
                            className="btn btn-outline-secondary"
                            value={gettext('Cancel')}
                            onClick={this.props.closeEditor}
                            disabled={this.state.saving}
                            aria-label={gettext('Cancel')}
                        />
                        <input
                            type="button"
                            className="btn btn-outline-primary"
                            value={gettext('Save')}
                            onClick={this.saveTopic}
                            disabled={this.state.saving || !this.state.valid}
                            aria-label={gettext('Save')}
                        />
                    </div>
                )}
            </div>
        );
    }
}

TopicEditor.propTypes = {
    topic: types.topic,
    userId: PropTypes.string,
    isLoading: PropTypes.bool,
    navigations: PropTypes.arrayOf(PropTypes.object),
    fetchNavigations: PropTypes.func,
    closeEditor: PropTypes.func,
    saveTopic: PropTypes.func,
    onTopicChanged: PropTypes.func,
    hideModal: PropTypes.func,
    loadMyTopic: PropTypes.func,
    editorFullscreen: PropTypes.bool,
    setTopicEditorFullscreen: PropTypes.func,
    globalTopicsEnabled: PropTypes.bool,
    isAdmin: PropTypes.bool,
    companyUsers: PropTypes.array,
    user: PropTypes.object,
};

const mapStateToProps = (state: any) => ({
    userId: get(state, 'editedUser._id'),
    isLoading: state.isLoading,
    navigations: state.navigations || [],
    editorFullscreen: topicEditorFullscreenSelector(state),
    companyUsers: state.monitoringProfileUsers || [],
});

const mapDispatchToProps = (dispatch: any) => ({
    fetchNavigations: () => dispatch(fetchNavigations()),
    hideModal: () => dispatch(hideModal()),
    saveTopic: (isExisting: any, topic: any) => isExisting ?
        dispatch(submitProfileFollowTopic(topic)) :
        dispatch(submitWireFollowTopic(topic)),
    loadMyTopic: (topic: any) => topic.topic_type === 'agenda' ?
        dispatch(loadMyAgendaTopic(topic._id)) :
        dispatch(loadMyWireTopic(topic._id)),
    setTopicEditorFullscreen: (fullscreen: any) => dispatch(setTopicEditorFullscreen(fullscreen)),
});

export default connect(mapStateToProps, mapDispatchToProps)(TopicEditor);
