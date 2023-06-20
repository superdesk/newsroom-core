import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

import TextInput from 'components/TextInput';
import CheckboxInput from 'components/CheckboxInput';
import {ToolTip} from 'ui/components/ToolTip';

import {gettext} from 'utils';

const TOPIC_NAME_MAXLENGTH = 30;

const TopicForm = ({original, topic, save, onChange, globalTopicsEnabled, onSubscribeChanged, readOnly}: any) => (
    <div>
        <form onSubmit={save}>
            {original._id == null ? null : (
                <div className="form-group">
                    <label htmlFor="notifications">{gettext('Email Notifications:')}</label>
                    <div className="field">
                        <ToolTip>
                            <button
                                type="button"
                                className={classNames(
                                    'btn',
                                    {
                                        'btn-primary': topic.notifications,
                                        'btn-outline-primary': !topic.notifications
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
            )}
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
        </form>
    </div>
);

TopicForm.propTypes = {
    original: PropTypes.object.isRequired,
    topic: PropTypes.object.isRequired,
    globalTopicsEnabled: PropTypes.bool.isRequired,
    onChange: PropTypes.func.isRequired,
    onSubscribeChanged: PropTypes.func.isRequired,
    save: PropTypes.func.isRequired,
    readOnly: PropTypes.bool,
};

export default TopicForm;
