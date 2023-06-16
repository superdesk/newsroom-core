import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

import {gettext} from 'utils';

import TextInput from 'components/TextInput';
import CheckboxInput from 'components/CheckboxInput';
import {ToolTip} from 'ui/components/ToolTip';

import {Dropdown} from 'components/Dropdown';
import {FormSection} from 'components/FormSection';

import TopicParameters from './TopicParameters';

const TOPIC_NAME_MAXLENGTH = 30;

const getFolderName = (topic, folders) => {
    const folder = topic.folder ? folders.find((folder) => folder._id == topic.folder) : null;

    return folder ? folder.name : gettext('Add to folder');
};

const TopicForm = ({original, topic, save, onChange, globalTopicsEnabled, onSubscribeChanged, readOnly, folders, onFolderChange}) => (
    <form onSubmit={save}>
        <div className="nh-flex-container list-item__preview-form pt-0">
            <div className="nh-flex__row">
                <div className="nh-flex__column">
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
                    <FormSection name={gettext('Email Notifications:')}>
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
                <FormSection name={gettext('Organize your Topic')}>
                    <div className="nh-container nh-container--direction-row mb-3 pt-2 pb-3">
                        <Dropdown
                            small={true}
                            stretch={true}
                            icon={'icon--folder'}
                            label={getFolderName(topic, folders)}
                        >
                            <button
                                key={'top'}
                                type="button"
                                className='dropdown-item'
                                onClick={() => onFolderChange(null)}
                            >{gettext('Top level')}</button>
                            {folders.map((folder) => (
                                <button key={folder._id}
                                    type="button"
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
                <FormSection name={gettext('Topic details')}>
                    <TopicParameters
                        topic={topic}
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
};

export default TopicForm;
