import React from 'react';
import classNames from 'classnames';

import {IUser, ITopic, ITopicFolder, INavigation, IFilterGroup, ITopicNotificationScheduleType} from 'interfaces';
import {gettext, getSubscriptionTimesString} from 'utils';

import TextInput from 'components/TextInput';
import CheckboxInput from 'components/CheckboxInput';

import {Dropdown} from 'components/Dropdown';
import {FormSection} from 'components/FormSection';

import {SearchResultTagsList} from './SearchResultsBar/SearchResultTagsList';

const TOPIC_NAME_MAXLENGTH = 30;

function getFolderName(topic: ITopic, folders: Array<ITopicFolder>): string {
    const folder = topic.folder ? folders.find((folder: any) => folder._id === topic.folder) : null;

    return folder ? folder.name : gettext('Add to folder');
}

function getSubscriptionNotificationType(topic: ITopic, userId: IUser['_id']): ITopicNotificationScheduleType {
    const subscriber = (topic.subscribers || []).find(
        (subscriber) => subscriber.user_id === userId
    );

    return subscriber == null ?
        null :
        subscriber.notification_type;
}


interface IProps {
    original: ITopic;
    topic: ITopic;
    user: IUser;
    globalTopicsEnabled: boolean;
    readOnly: boolean;
    folders: Array<ITopicFolder>;
    navigations: {[key: string]: INavigation};
    filterGroups: {[key: string]: IFilterGroup};
    availableFields: Array<string>;

    onChange(field: string): (event: React.ChangeEvent<HTMLInputElement>) => void;
    save(event: React.FormEvent<HTMLFormElement>): void;
    onFolderChange(folder: ITopicFolder | null): void;
    toggleNavigation(navigation: INavigation): void;
    clearSearchQuery(): void;
    toggleAdvancedSearchField(field: string): void;
    setAdvancedSearchKeywords(field: string, keywords: string): void;
    clearAdvancedSearchParams(): void;
    toggleFilter(key: string, value: any): void;
    setCreatedFilter(createdFilter: ITopic['created']): void;
    resetFilter(): void;

    changeNotificationType(notificationType: ITopicNotificationScheduleType): void;
    openEditTopicNotificationsModal(): void;
}

const TopicForm: React.FC<IProps> = ({
    original,
    topic,
    save,
    onChange,
    globalTopicsEnabled,
    readOnly,
    folders,
    onFolderChange,
    user,
    navigations,
    filterGroups,
    toggleNavigation,
    clearSearchQuery,
    toggleAdvancedSearchField,
    setAdvancedSearchKeywords,
    clearAdvancedSearchParams,
    toggleFilter,
    setCreatedFilter,
    resetFilter,
    availableFields,
    changeNotificationType,
    openEditTopicNotificationsModal,
}): React.ReactElement => {
    const topicSubscriptionType = getSubscriptionNotificationType(topic, user._id);

    return (
        <form onSubmit={save}>
            <div className="nh-flex-container list-item__preview-form pt-0">
                <div className="nh-flex__row">
                    <div className="nh-flex__column" data-test-id="topic-form-group--details">
                        <TextInput
                            name="name"
                            label={gettext('Name')}
                            required={true}
                            value={topic.label}
                            onChange={onChange('label')}
                            maxLength={TOPIC_NAME_MAXLENGTH}
                            autoFocus={true}
                            readOnly={readOnly}
                        />
                        {!(globalTopicsEnabled && (original._id == null || original.user)) ? null : (
                            <CheckboxInput
                                name="is_global"
                                label={gettext('Share with my Company')}
                                value={topic.is_global || false}
                                onChange={onChange('is_global')}
                                readOnly={readOnly}
                            />
                        )}
                        {!(original._id != null && original.user == null) ? null : (
                            <label htmlFor={original._id}>{gettext('Created Externally')}</label>
                        )}
                    </div>
                </div>
                <div className="nh-flex__row">
                    <FormSection name={gettext('Email Notifications:')} testId="topic-form-group--notifications">
                        <div>
                            <div className="toggle-button__group toggle-button__group--spaced toggle-button__group--stretch-items my-2">
                                <button
                                    type="button"
                                    className={classNames(
                                        'toggle-button toggle-button--small',
                                        {'toggle-button--active': topicSubscriptionType == null}
                                    )}
                                    onClick={() => changeNotificationType(null)}
                                >
                                    {gettext('None')}
                                </button>
                                <button
                                    type="button"
                                    className={classNames(
                                        'toggle-button toggle-button--small',
                                        {'toggle-button--active': topicSubscriptionType === 'real-time'}
                                    )}
                                    onClick={() => changeNotificationType('real-time')}
                                >
                                    {gettext('Real-Time')}
                                </button>
                                <button
                                    type="button"
                                    className={classNames(
                                        'toggle-button toggle-button--small',
                                        {'toggle-button--active': topicSubscriptionType === 'scheduled'}
                                    )}
                                    onClick={() => changeNotificationType('scheduled')}
                                >
                                    {gettext('Scheduled')}
                                </button>
                            </div>
                            <div className="nh-container nh-container--highlight mb-3">
                                <p className="nh-container__text--small">
                                    {gettext('Your saved topic results will be emailed in a digest format at the time(s) per day set below.')}
                                </p>
                                <div className="h-spacer h-spacer--medium" />
                                <span className="nh-container__schedule-info mb-3">
                                    {getSubscriptionTimesString(user)}
                                </span>
                                <button
                                    type="button"
                                    className="nh-button nh-button--small nh-button--tertiary"
                                    onClick={openEditTopicNotificationsModal}
                                >
                                    {gettext('Edit schedule')}
                                </button>
                            </div>
                        </div>
                    </FormSection>
                    <FormSection name={gettext('Organize your Topic')} testId="topic-form-group--folder">
                        <div className="nh-container nh-container--direction-row mb-3 pt-2 pb-3">
                            <Dropdown
                                small={true}
                                stretch={true}
                                icon={'icon--folder'}
                                label={getFolderName(topic, folders)}
                            >
                                {readOnly !== true && topic.folder && (
                                    <button
                                        key="top"
                                        type="button"
                                        data-test-id="dropdown-item--remove-from-folder"
                                        className='dropdown-item'
                                        onClick={() => onFolderChange(null)}
                                    >{gettext('Remove from folder')}</button>
                                )}
                                {readOnly !== true && folders.map((folder: any) => (
                                    <button
                                        key={folder._id}
                                        type="button"
                                        data-test-id={`dropdown-item--${folder.name}`}
                                        className="dropdown-item"
                                        onClick={() => onFolderChange(folder)}
                                        disabled={readOnly}
                                    >
                                        {folder.name}
                                    </button>
                                ))}
                            </Dropdown>
                        </div>
                    </FormSection>
                </div>
                <div className="nh-flex__row">
                    <FormSection name={gettext('Topic details')} testId="topic-form-group--params">
                        <SearchResultTagsList
                            user={user}
                            readonly={true}
                            showSaveTopic={false}
                            showMyTopic={false}
                            searchParams={topic}
                            activeTopic={topic}
                            topicType={topic.topic_type}
                            navigations={navigations}
                            filterGroups={filterGroups}
                            toggleNavigation={toggleNavigation}
                            setQuery={clearSearchQuery}
                            toggleAdvancedSearchField={toggleAdvancedSearchField}
                            setAdvancedSearchKeywords={setAdvancedSearchKeywords}
                            clearAdvancedSearchParams={clearAdvancedSearchParams}
                            toggleFilter={toggleFilter}
                            setCreatedFilter={setCreatedFilter}
                            resetFilter={resetFilter}
                            availableFields={availableFields}
                        />
                    </FormSection>
                </div>
            </div>
        </form>
    );
};

export default TopicForm;
