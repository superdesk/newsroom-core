import React from 'react';
import {connect} from 'react-redux';
import {get, set, cloneDeep, isEqual} from 'lodash';
import classNames from 'classnames';

import {IUser, ITopic, ITopicFolder, INavigation, IFilterGroup, ITopicNotificationScheduleType} from 'interfaces';
import {gettext, notify} from 'utils';
import {canUserEditTopic} from 'topics/utils';

import {topicEditorFullscreenSelector, sectionSelector} from 'user-profile/selectors';
import {filterGroupsByIdSelector, navigationsByIdSelector} from '../selectors';
import {getAdvancedSearchFields} from '../utils';

import {fetchNavigations} from 'navigations/actions';
import {submitFollowTopic as submitWireFollowTopic} from 'search/actions';
import {
    submitFollowTopic as submitProfileFollowTopic,
    hideModal,
    setTopicEditorFullscreen,
    openEditTopicNotificationsModal,
    setTopicSubscribers,
    saveFolder,
} from 'user-profile/actions';
import {loadMyWireTopic} from 'wire/actions';
import {loadMyAgendaTopic} from 'agenda/actions';

import TopicForm from './TopicForm';
import EditPanel from 'components/EditPanel';
import AuditInformation from 'components/AuditInformation';
import {ToolTip} from 'ui/components/ToolTip';

interface IProps {
    topic: ITopic;
    userId: IUser['_id'];
    user: IUser;
    companyUsers: Array<IUser>;
    isLoading: boolean;
    navigations: Array<INavigation>;
    navigationsById: {[id: string]: INavigation};
    editorFullscreen: boolean;
    globalTopicsEnabled: boolean;
    isAdmin: boolean;
    section: 'wire' | 'agenda' | 'monitoring';
    filterGroups: {[key: string]: IFilterGroup};
    availableFields: Array<string>;

    saveFolder: (folder: any, data: any, global?: boolean) => void;
    fetchNavigations(): Promise<void>;
    closeEditor(): void;
    saveTopic(isExisting: boolean, topic: ITopic): Promise<ITopic>;
    onTopicChanged(): void;
    hideModal(): void;
    loadMyTopic(topic: ITopic): void;
    setTopicEditorFullscreen(fullscreen: boolean): void;
    openEditTopicNotificationsModal(): void;
    setTopicSubscribers(topic: ITopic, subscribers: ITopic['subscribers']): void;
    folders: {
        companyFolders: Array<ITopicFolder>;
        userFolders: Array<ITopicFolder>;
    };
}

interface IState {
    topic: ITopic;
    saving: boolean;
    valid: boolean;
    tabs: Array<{
        label: string;
        name: string;
        tooltip: string;
    }>;
    activeTab: string;
}

class TopicEditor extends React.Component<IProps, IState> {
    static propTypes: any;
    constructor(props: any) {
        super(props);

        this.state = {
            topic: this.props.topic,
            saving: false,
            valid: false,
            tabs: [],
            activeTab: 'topic',
        };

        this.onChangeHandler = this.onChangeHandler.bind(this);
        this.saveTopic = this.saveTopic.bind(this);
        this.handleTabClick = this.handleTabClick.bind(this);
        this.onFolderChange = this.onFolderChange.bind(this);

        this.toggleNavigation = this.toggleNavigation.bind(this);
        this.clearSearchQuery = this.clearSearchQuery.bind(this);
        this.toggleAdvancedSearchField = this.toggleAdvancedSearchField.bind(this);
        this.setAdvancedSearchKeywords = this.setAdvancedSearchKeywords.bind(this);
        this.clearAdvancedSearchParams = this.clearAdvancedSearchParams.bind(this);
        this.toggleFilter = this.toggleFilter.bind(this);
        this.setCreatedFilter = this.setCreatedFilter.bind(this);
        this.resetFilter = this.resetFilter.bind(this);
        this.changeUserNotifications = this.changeUserNotifications.bind(this);
        this.changeNotificationType = this.changeNotificationType.bind(this);
    }

    componentDidMount() {
        this.props.fetchNavigations();

        if (this.props.topic != null) {
            this.changeTopic(this.props.topic);
        }
    }

    componentDidUpdate(prevProps: Readonly<IProps>) {
        if (get(prevProps, 'topic._id') !== get(this.props, 'topic._id') ||
            get(prevProps, 'topic._etag') !== get(this.props, 'topic._etag')
        ) {
            this.changeTopic(this.props.topic);
        }
    }

    handleTabClick(tabName: string) {
        this.setState({activeTab: tabName});
    }

    changeTopic(topic: ITopic) {
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

    getTabsForTopic(topic: ITopic) {
        return (!topic._id || !topic.is_global || !this.props.isAdmin) ?
            [] :
            [
                {label: gettext('Company Topic'), name: 'topic', tooltip: gettext('Edit Metadata')},
                {label: gettext('Subscribers'), name: 'subscribers', tooltip: gettext('Email Notifications')},
            ];
    }

    updateFormValidity(topic: ITopic) {
        const original = get(this.props, 'topic') || {};
        const isDirty = [
            'label',
            'is_global',
            'folder',
            'navigation',
            'query',
            'advanced',
            'filter',
            'created'
        ].some((field) => get(original, field) !== get(topic, field))
            || !isEqual(original.subscribers, topic.subscribers);

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
            const value = field === 'is_global' ?
                !get(topic, field) :
                event.target.value;

            if (field === 'is_global') {
                topic.folder = null;
            }

            set(topic, field, value);
            this.setState({topic});
            this.updateFormValidity(topic);
        };
    }

    changeUserNotifications(event: React.ChangeEvent<HTMLInputElement>) {
        const topic = cloneDeep(this.state.topic);
        const originalUserIds = (topic.subscribers || []).map((subscriber) => subscriber.user_id);
        const newUserIds = event.target.value as any as Array<string>;

        // Remove users
        topic.subscribers = (topic.subscribers || []).filter((subscriber) => (
            newUserIds.includes(subscriber.user_id)
        ));

        // Add useres
        newUserIds.forEach((userId) => {
            if (!originalUserIds.includes(userId)) {
                topic.subscribers.push({
                    user_id: userId,
                    notification_type: 'real-time',
                });
            }
        });

        this.setState({topic});
        this.updateFormValidity(topic);
    }

    changeNotificationType(notificationType: ITopicNotificationScheduleType) {
        const topic = cloneDeep(this.state.topic);

        if (topic.subscribers == null) {
            topic.subscribers = [];
        }

        // If notificationType == null, then remove this user from the Topic subscriber list
        if (notificationType === null) {
            topic.subscribers = topic.subscribers.filter(
                (subscriber) => subscriber.user_id !== this.props.userId
            );
        } else {
            const subscriber = topic.subscribers.find(
                (subscriber) => subscriber.user_id === this.props.userId
            );

            if (subscriber == null) {
                // Not currently enabled
                topic.subscribers.push({
                    user_id: this.props.userId,
                    notification_type: notificationType,
                });
            } else {
                subscriber.notification_type = notificationType;
            }
        }

        if (topic._id != null && !canUserEditTopic(topic, this.props.user)) {
            this.props.setTopicSubscribers(topic, topic.subscribers);
        } else {
            this.setState({topic});
            this.updateFormValidity(topic);
        }
    }

    onFolderChange(folder: ITopicFolder | null) {
        const topic = cloneDeep(this.state.topic);

        topic.folder = folder ? folder._id : null;

        this.setState({topic});
        this.updateFormValidity(topic);
    }

    saveTopic(event: any) {
        const topic = cloneDeep(this.state.topic);
        const isExisting = !this.isNewTopic();

        event.preventDefault && event.preventDefault();
        this.setState({saving: true});
        this.props.saveTopic(
            isExisting,
            topic
        )
            .then((savedTopic) => {
                this.setState({saving: false});
                this.props.onTopicChanged();
                this.props.closeEditor();

                if (isExisting) {
                    notify.success(gettext('Topic updated successfully'));
                } else {
                    notify.success(gettext('Topic created successfully'));

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
            return gettext('Create new Topic');
        } else {
            return gettext('Save Topic');
        }
    }

    toggleNavigation(navigation: INavigation) {
        this.setState((prevState: any) => ({
            topic: {
                ...prevState.topic,
                navigation: prevState.topic.navigation.filter((navId: any) => navId !== navigation._id)
            },
        }), () => {
            if (this.state.topic != null) {
                // This should not happen
                this.updateFormValidity(this.state.topic);
            }
        });
    }

    clearSearchQuery() {
        this.setState((prevState: any) => ({
            topic: {
                ...prevState.topic,
                query: '',
            },
        }), () => {
            this.updateFormValidity(this.state.topic);
        });
    }

    toggleAdvancedSearchField(field: string) {
        this.setState((prevState: Readonly<IState>) => {
            const topic = cloneDeep(prevState.topic);

            if (topic.advanced == null) {
                topic.advanced = {
                    fields: [],
                    all: '',
                    any: '',
                    exclude: '',
                };
            }

            topic.advanced.fields = topic.advanced.fields.includes(field) ?
                topic.advanced.fields.filter((fieldName) => fieldName !== field) :
                [...topic.advanced.fields, field];

            if (!topic.advanced.fields.length) {
                // At least 1 field must be selected
                return null;
            }

            return {topic: topic};
        }, () => {
            this.updateFormValidity(this.state.topic);
        });
    }

    setAdvancedSearchKeywords(field: string, keywords: string) {
        this.setState((prevState: any) => ({
            topic: {
                ...prevState.topic,
                advanced: {
                    ...prevState.topic.advanced,
                    [field]: keywords,
                },
            },
        }), () => {
            this.updateFormValidity(this.state.topic);
        });
    }

    clearAdvancedSearchParams() {
        this.setState((prevState: any) => ({
            topic: {
                ...prevState.topic,
                advanced: {
                    all: '',
                    any: '',
                    exclude: '',
                    fields: ['headline', 'slugline', 'body_html'],
                },
            },
        }), () => {
            this.updateFormValidity(this.state.topic);
        });
    }

    toggleFilter(key: string, value: any) {
        this.setState((prevState: any) => ({
            topic: {
                ...prevState.topic,
                filter: {
                    ...prevState.topic.filter,
                    [key]: prevState.topic.filter[key].filter((filterValue: any) => filterValue !== value),
                },
            },
        }), () => {
            this.updateFormValidity(this.state.topic);
        });
    }

    setCreatedFilter(createdFilter: ITopic['created']) {
        this.setState((prevState: any) => ({
            topic: {
                ...prevState.topic,
                created: createdFilter,
            },
        }), () => {
            this.updateFormValidity(this.state.topic);
        });
    }

    resetFilter() {
        this.setState((prevState: any) => ({
            topic: {
                ...prevState.topic,
                filter: null,
                created: null,
            },
        }), () => {
            this.updateFormValidity(this.state.topic);
        });
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
            <div
                role="dialog"
                aria-label={this.getTitle()}
                data-test-id="user-topic-editor"
                className={showTabs ? 'list-item__preview' : containerClasses}
            >
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
                        <i className="icon--close-thin" />
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
                                        className={`nav-link ${this.state.activeTab === tab.name && 'active'}`}
                                        href='#'
                                        title={tab.tooltip}
                                        onClick={() => this.handleTabClick(tab.name)}
                                    >
                                        {tab.label}
                                    </a>
                                </ToolTip>
                            </li>
                        ))}
                    </ul>
                )}
                <div className="list-item__preview-content">
                    {this.state.activeTab === 'topic' && updatedTopic && (
                        <React.Fragment>
                            <TopicForm
                                saveFolder={this.props.saveFolder}
                                original={originalTopic}
                                globalTopicsEnabled={this.props.globalTopicsEnabled}
                                topic={updatedTopic}
                                save={this.saveTopic}
                                onChange={this.onChangeHandler}
                                readOnly={isReadOnly}
                                folders={
                                    this.state.topic.is_global
                                        ? this.props.folders.companyFolders
                                        : this.props.folders.userFolders
                                }
                                onFolderChange={this.onFolderChange}

                                user={this.props.user}
                                navigations={this.props.navigationsById}
                                filterGroups={this.props.filterGroups}

                                toggleNavigation={this.toggleNavigation}
                                clearSearchQuery={this.clearSearchQuery}
                                toggleAdvancedSearchField={this.toggleAdvancedSearchField}
                                setAdvancedSearchKeywords={this.setAdvancedSearchKeywords}
                                clearAdvancedSearchParams={this.clearAdvancedSearchParams}
                                toggleFilter={this.toggleFilter}
                                setCreatedFilter={this.setCreatedFilter}
                                resetFilter={this.resetFilter}
                                availableFields={this.props.availableFields}
                                changeNotificationType={this.changeNotificationType}
                                openEditTopicNotificationsModal={this.props.openEditTopicNotificationsModal}
                            />
                        </React.Fragment>
                    )}
                    {this.state.activeTab === 'subscribers' && updatedTopic && (
                        <EditPanel
                            parent={{
                                subscribers: (updatedTopic.subscribers || [])
                                    .map((subscriber) => subscriber.user_id)
                            }}
                            items={this.props.companyUsers.map((user: any) => ({
                                ...user,
                                name: `${user.first_name} ${user.last_name}`,
                            }))}
                            field="subscribers"
                            onChange={this.changeUserNotifications}
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
                            className="nh-button nh-button--secondary"
                            value={gettext('Cancel')}
                            onClick={this.props.closeEditor}
                            disabled={this.state.saving}
                            aria-label={gettext('Cancel')}
                        />
                        <input
                            data-test-id="save-topic-btn"
                            type="button"
                            className="nh-button nh-button--primary"
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

const mapStateToProps = (state: any) => ({
    userId: get(state, 'editedUser._id'),
    isLoading: state.isLoading,
    navigations: state.navigations || [],
    editorFullscreen: topicEditorFullscreenSelector(state),
    companyUsers: state.monitoringProfileUsers || [],

    navigationsById: navigationsByIdSelector(state),
    filterGroups: filterGroupsByIdSelector(state),
    availableFields: getAdvancedSearchFields(sectionSelector(state)),
    section: sectionSelector(state),
});

const mapDispatchToProps = (dispatch: any) => ({
    saveFolder: (folder: any, data: any, global?: boolean) => dispatch(saveFolder(folder, data, global)),
    fetchNavigations: () => dispatch(fetchNavigations()),
    hideModal: () => dispatch(hideModal()),
    saveTopic: (isExisting: any, topic: any) => isExisting ?
        dispatch(submitProfileFollowTopic(topic)) :
        dispatch(submitWireFollowTopic(topic)),
    loadMyTopic: (topic: any) => topic.topic_type === 'agenda' ?
        dispatch(loadMyAgendaTopic(topic._id)) :
        dispatch(loadMyWireTopic(topic._id)),
    setTopicEditorFullscreen: (fullscreen: boolean) => dispatch(setTopicEditorFullscreen(fullscreen)),
    openEditTopicNotificationsModal: () => dispatch(openEditTopicNotificationsModal()),
    setTopicSubscribers: (topic: ITopic, subscribers: ITopic['subscribers']) =>
        dispatch(setTopicSubscribers(topic, subscribers)),
});

const component: React.ComponentType<any> = connect(mapStateToProps, mapDispatchToProps)(TopicEditor);

export default component;
