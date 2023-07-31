import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {get, set, cloneDeep, isEqual} from 'lodash';
import classNames from 'classnames';

import {gettext, notify} from 'utils';
import {canUserEditTopic} from 'topics/utils';
import types from 'wire/types';

import {topicEditorFullscreenSelector, sectionSelector} from 'user-profile/selectors';
import {filterGroupsByIdSelector, navigationsByIdSelector} from '../selectors';
import {getAdvancedSearchFields} from '../utils';

import {fetchNavigations} from 'navigations/actions';
import {submitFollowTopic as submitWireFollowTopic, subscribeToTopic, unsubscribeToTopic} from 'search/actions';
import {submitFollowTopic as submitProfileFollowTopic, hideModal, setTopicEditorFullscreen, fetchFolders} from 'user-profile/actions';
import {loadMyWireTopic} from 'wire/actions';
import {loadMyAgendaTopic} from 'agenda/actions';

import TopicForm from './TopicForm';
import EditPanel from 'components/EditPanel';
import AuditInformation from 'components/AuditInformation';
import {ToolTip} from 'ui/components/ToolTip';

class TopicEditor extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            topic: null,
            saving: false,
            valid: false,
            tabs: [],
            activeTab: 'topic',
            folders: [],
        };

        this.onChangeHandler = this.onChangeHandler.bind(this);
        this.onSubscribeChanged = this.onSubscribeChanged.bind(this);
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
    }

    componentDidMount() {
        this.props.fetchNavigations();
        this.reloadFolders(this.props.topic != null && this.props.topic.is_global);

        if (this.props.topic != null) {
            this.changeTopic(this.props.topic);
        }
    }

    componentDidUpdate(prevProps) {
        if (get(prevProps, 'topic._id') !== get(this.props, 'topic._id')) {
            this.changeTopic(this.props.topic);
        }
    }

    handleTabClick(event) {
        this.setState({activeTab: event.target.name});
    }

    changeTopic(topic) {
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

    getTabsForTopic(topic) {
        return (!topic._id || !topic.is_global || !this.props.isAdmin) ?
            [] :
            [
                {label: gettext('Company Topic'), name: 'topic', tooltip: gettext('Edit Metadata')},
                {label: gettext('Subscribers'), name: 'subscribers', tooltip: gettext('Email Notifications')},
            ];
    }

    updateFormValidity(topic) {
        const original = get(this.props, 'topic') || {};
        const isDirty = [
            'label',
            'notifications',
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

    onChangeHandler(field) {
        return (event) => {
            const topic = cloneDeep(this.state.topic);
            const value = ['notifications', 'is_global'].includes(field) ?
                !get(topic, field) :
                event.target.value;

            if (field === 'is_global') {
                topic.folder = null;
                this.reloadFolders(value);
            }

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
            topic.subscribers = (topic.subscribers || []).filter((userId) => userId !== this.props.userId);
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

    onFolderChange(folder) {
        const topic = {...this.state.topic};

        topic.folder = folder ? folder._id : null;

        this.setState({topic});
        this.updateFormValidity(topic);
    }

    saveTopic(event) {
        const original = this.props.topic;
        const topic = cloneDeep(this.state.topic);
        const isExisting = !this.isNewTopic();

        // Construct new list of subscribers
        if (!isExisting || !original.is_global) {
            let subscribers = topic.subscribers || [];
            const alreadySubscribed = subscribers.includes(this.props.userId);

            if (topic.notifications && !alreadySubscribed) {
                subscribers.push(this.props.userId);
            } else if (!topic.notifications && alreadySubscribed) {
                subscribers = subscribers.filter(
                    (userId) => userId !== this.props.userId
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

    toggleNavigation(navigation) {
        this.setState((prevState) => ({
            topic: {
                ...prevState.topic,
                navigation: prevState.topic.navigation.filter((navId) => navId !== navigation._id)
            },
        }), () => {
            this.updateFormValidity(this.state.topic);
        });
    }

    clearSearchQuery() {
        this.setState((prevState) => ({
            topic: {
                ...prevState.topic,
                query: '',
            },
        }), () => {
            this.updateFormValidity(this.state.topic);
        });
    }

    toggleAdvancedSearchField(field) {
        this.setState((prevState) => {
            const topic = cloneDeep(prevState.topic);

            topic.advanced.fields = (topic.advanced.fields || []).includes(field) ?
                topic.advanced.fields.filter((fieldName) => fieldName !== field) :
                [...topic.advanced.fields, field];

            if (!topic.advanced.fields.length) {
                // At least 1 field must be selected
                return {};
            }

            return {topic: topic};
        }, () => {
            this.updateFormValidity(this.state.topic);
        });
    }

    setAdvancedSearchKeywords(field, keywords) {
        this.setState((prevState) => ({
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
        this.setState((prevState) => ({
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

    toggleFilter(key, value) {
        this.setState((prevState) => ({
            topic: {
                ...prevState.topic,
                filter: {
                    ...prevState.topic.filter,
                    [key]: prevState.topic.filter[key].filter((filterValue) => filterValue !== value),
                },
            },
        }), () => {
            this.updateFormValidity(this.state.topic);
        });
    }

    setCreatedFilter(createdFilter) {
        this.setState((prevState) => ({
            topic: {
                ...prevState.topic,
                created: createdFilter,
            },
        }), () => {
            this.updateFormValidity(this.state.topic);
        });
    }

    resetFilter() {
        this.setState((prevState) => ({
            topic: {
                ...prevState.topic,
                filter: null,
                created: null,
            },
        }), () => {
            this.updateFormValidity(this.state.topic);
        });
    }

    reloadFolders(global) {
        this.props.fetchFolders(global).then((folders) => {
            this.setState({folders: folders.filter((folder) => folder.section === this.props.section)});
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
                        {this.state.tabs.map((tab) => (
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
                <div className="list-item__preview-content">
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
                                folders={this.state.folders}
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
                            />
                        </React.Fragment>
                    )}
                    {this.state.activeTab === 'subscribers' && updatedTopic && (
                        <EditPanel
                            parent={updatedTopic}
                            items={this.props.companyUsers.map((user) => ({
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

TopicEditor.propTypes = {
    topic: types.topic,
    userId: PropTypes.string,
    isLoading: PropTypes.bool,
    navigations: PropTypes.arrayOf(PropTypes.object),
    navigationsById: PropTypes.object,
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
    fetchFolders: PropTypes.func,
    section: PropTypes.string,

    filterGroups: PropTypes.object,
    availableFields: PropTypes.arrayOf(PropTypes.string).isRequired,
};

const mapStateToProps = (state) => ({
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

const mapDispatchToProps = (dispatch) => ({
    fetchNavigations: () => dispatch(fetchNavigations()),
    hideModal: () => dispatch(hideModal()),
    saveTopic: (isExisting, topic) => isExisting ?
        dispatch(submitProfileFollowTopic(topic)) :
        dispatch(submitWireFollowTopic(topic)),
    loadMyTopic: (topic) => topic.topic_type === 'agenda' ?
        dispatch(loadMyAgendaTopic(topic._id)) :
        dispatch(loadMyWireTopic(topic._id)),
    setTopicEditorFullscreen: (fullscreen) => dispatch(setTopicEditorFullscreen(fullscreen)),
    fetchFolders: (global) => dispatch(fetchFolders(global, true)),
});

export default connect(mapStateToProps, mapDispatchToProps)(TopicEditor);
