import React, {useState} from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

import {gettext} from 'utils';

export function TopicFolderEditor ({folder, onSave, onCancel, error}) {
    const [name, setName] = useState(folder.name || '');

    return (
        <div className={classNames('simple-card__group-header', {'simple-card__group-header--selected': error})}>
            <div className="d-flex flex-row flex-grow-1 align-items-center gap-2 ps-1">
                <i className="icon--folder icon--small"></i>
                <input type="text"
                    aria-label={gettext('Folder name')}
                    className="form-control form-control--small"
                    maxLength="30"
                    placeholder={gettext('Folder Name')}
                    value={name}
                    onChange={(event) => {
                        setName(event.target.value || '');
                    }}
                />
                <button type="button"
                    className="icon-button icon-button--secondary icon-button--bordered icon-button--small"
                    aria-label={gettext('Cancel')}
                    title={gettext('Cancel')}
                    onClick={() => onCancel()}
                ><i className="icon--close-thin"></i></button>
                <button type="button"
                    className="icon-button icon-button--primary icon-button--bordered icon-button--small"
                    aria-label={gettext('Save')}
                    title={gettext('Save')}
                    onClick={() => {
                        onSave(name);
                    }}><i className="icon--check"></i></button>
            </div>
        </div>
    );
}

TopicFolderEditor.propTypes = {
    folder: PropTypes.shape({
        name: PropTypes.string,
    }),
    error: PropTypes.object,
    onSave: PropTypes.func,
    onCancel: PropTypes.func,
};
