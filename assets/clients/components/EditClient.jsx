import React from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';

import TextInput from 'components/TextInput';
import {gettext} from 'utils';

class EditClient extends React.Component {
    constructor(props) {
        super(props);
    }


    render() {
        return (
            <div className={classNames('list-item__preview')}
                role={gettext('dialog')}
                aria-label={gettext('Edit Client')}>
                <div className='list-item__preview-header'>
                    <h3>{ gettext('Add/Edit Client') }</h3>
                    <button
                        id='hide-sidebar'
                        type='button'
                        className='icon-button'
                        data-dismiss='modal'
                        aria-label={gettext('Close')}
                        onClick={this.props.onClose}>
                        <i className="icon--close-thin icon--gray" aria-hidden='true'></i>
                    </button>
                </div>

                <div className='tab-content'>
                    <div className='tab-pane active' id='client-details'>
                        <form>
                            <div className="list-item__preview-form">
                                <TextInput
                                    name='name'
                                    label={gettext('Name')}
                                    value={this.props.client.name}
                                    onChange={this.props.onChange}
                                />
                            </div>
                            <div className='list-item__preview-footer'>
                                <input
                                    type='button'
                                    className='btn btn-outline-primary'
                                    value={gettext('Save')}
                                    onClick={this.props.onSave}/>
                                {this.props.client._id && <input
                                    type='button'
                                    className='btn btn-outline-secondary'
                                    value={gettext('Delete')}
                                    onClick={this.props.onDelete}/>}
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        );
    }
}

EditClient.propTypes = {
    client: PropTypes.object.isRequired,
    onChange: PropTypes.func,
    onSave: PropTypes.func.isRequired,
    onClose: PropTypes.func.isRequired,
    onDelete: PropTypes.func.isRequired,
};

export default EditClient;
