import React from 'react';
import PropTypes from 'prop-types';

import TextInput from 'components/TextInput';
import CheckboxInput from 'components/CheckboxInput';

import {gettext} from 'utils';

const TOPIC_NAME_MAXLENGTH = 30;

const TopicForm = ({original, topic, save, onChange, globalTopicsEnabled, onSubscribeChanged, readOnly, showSubscribeButton}) => (
    <div>
        <form onSubmit={save}>
            {showSubscribeButton && (
                <div className="form-group">
                    <input
                        name="notifications"
                        type="button"
                        className="btn btn-outline-primary"
                        value={(topic.notifications || false) ? gettext('Unsubscribe') : gettext('Subscribe')}
                        onClick={onSubscribeChanged}
                    />
                </div>
            )}
            <TextInput
                label={gettext('Name')}
                required={true}
                value={topic.label}
                onChange={onChange('label')}
                maxLength={TOPIC_NAME_MAXLENGTH}
                autoFocus={true}
                readOnly={readOnly}
            />
            {!(original._id == null || !original.is_global) ? null : (
                <CheckboxInput
                    label={gettext('Send me notifications')}
                    value={topic.notifications || false}
                    onChange={onChange('notifications')}
                    readOnly={readOnly}
                />
            )}
            {!(globalTopicsEnabled && original.user) ? null : (
                <CheckboxInput
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
    showSubscribeButton: PropTypes.bool,
};

export default TopicForm;
