import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

import {gettext} from 'utils';

import TextInput from 'components/TextInput';
import CheckboxInput from 'components/CheckboxInput';
import {ToolTip} from 'ui/components/ToolTip';

import {Dropdown} from 'components/Dropdown';
import {FormSection} from 'components/FormSection';

import {SearchResultTagsList} from './SearchResultsBar/SearchResultTagsList';

const TOPIC_NAME_MAXLENGTH = 30;

const getFolderName = (topic, folders) => {
    const folder = topic.folder ? folders.find((folder) => folder._id === topic.folder) : null;

    return folder ? folder.name : gettext('Add to folder');
};

const TopicForm = ({
    original,
    topic,
    save,
    onChange,
    globalTopicsEnabled,
    onSubscribeChanged,
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
}) => (
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
                    {original._id != null ? null : (
                        <CheckboxInput
                            name="notifications"
                            label={gettext('Send me notifications')}
                            value={topic.notifications || false}
                            onChange={onChange('notifications')}
                            readOnly={readOnly}
                        />
                    )}
                    {!(globalTopicsEnabled && (original._id == null || original.user)) ? null : (
                        <CheckboxInput
                            name="is_global"
                            label={gettext('Share with my Company')}
                            value={topic.is_global || false}
                            onChange={onChange('is_global')}
                            readOnly={readOnly}
                        />
                    )}
                    {!(original._id != null && original.user == null ) ? null : (
                        <label htmlFor={original._id}>{gettext('Created Externally')}</label>
                    )}
                </div>
            </div>
            <div className="nh-flex__row">
                {original._id == null ? null : (
                    <FormSection name={gettext('Email Notifications:')} testId="topic-form-group--notifications">
                        <div className="form-group">
                            <div className="field">
                                <ToolTip>
                                    <button
                                        type="button"
                                        className={classNames(
                                            'nh-button',
                                            {
                                                'nh-button--primary': topic.notifications,
                                                'nh-button--secondary': !topic.notifications
                                            }
                                        )}
                                        title={gettext('Toggle email notifications')}
                                        name="notifications"
                                        onClick={onSubscribeChanged}
                                    >
                                        {(topic.notifications || false) ? gettext('Unsubscribe') : gettext('Subscribe')}
                                    </button>
                                </ToolTip>
                            </div>
                        </div>
                    </FormSection>
                )}
                <FormSection name={gettext('Organize your Topic')} testId="topic-form-group--folder">
                    <div className="nh-container nh-container--direction-row mb-3 pt-2 pb-3">
                        <Dropdown
                            small={true}
                            stretch={true}
                            icon={'icon--folder'}
                            label={getFolderName(topic, folders)}
                        >
                            {topic.folder && (
                                <button
                                    key="top"
                                    type="button"
                                    data-test-id="dropdown-item--remove-from-folder"
                                    className='dropdown-item'
                                    onClick={() => onFolderChange(null)}
                                >{gettext('Remove from folder')}</button>
                            )}
                            {folders.map((folder) => (
                                <button
                                    key={folder._id}
                                    type="button"
                                    data-test-id={`dropdown-item--${folder.name}`}
                                    className="dropdown-item"
                                    onClick={() => onFolderChange(folder)}
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

TopicForm.propTypes = {
    original: PropTypes.object.isRequired,
    topic: PropTypes.object.isRequired,
    globalTopicsEnabled: PropTypes.bool.isRequired,
    onChange: PropTypes.func.isRequired,
    onSubscribeChanged: PropTypes.func.isRequired,
    save: PropTypes.func.isRequired,
    readOnly: PropTypes.bool,
    folders: PropTypes.array,
    onFolderChange: PropTypes.func,

    user: PropTypes.object,
    navigations: PropTypes.object,
    filterGroups: PropTypes.object,

    toggleNavigation: PropTypes.func,
    clearSearchQuery: PropTypes.func,
    toggleAdvancedSearchField: PropTypes.func,
    setAdvancedSearchKeywords: PropTypes.func,
    clearAdvancedSearchParams: PropTypes.func,
    toggleFilter: PropTypes.func,
    setCreatedFilter: PropTypes.func,
    resetFilter: PropTypes.func,
    availableFields: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default TopicForm;
