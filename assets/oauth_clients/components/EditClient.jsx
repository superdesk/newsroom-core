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
                        data-bs-dismiss='modal'
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
                                {this.props.client._id &&
                                    <TextInput
                                        name='client id'
                                        label={gettext('Client Id')}
                                        value={this.props.client._id}
                                    />
                                }
                                {this.props.client.secret_key &&
                                    <TextInput
                                        name='client secret'
                                        label={gettext('Client Secret')}
                                        value={this.props.client.secret_key}
                                        copyAction={true}
                                        description={gettext('Make sure to copy your new client secret now. You won`t be able to see it again.')}
                                    />
                                }
                            </div>
                            <div className='list-item__preview-footer'>
                                {this.props.client._id && <input
                                    type='button'
                                    className='nh-button nh-button--secondary'
                                    value={gettext('Delete')}
                                    onClick={this.props.onDelete}/>}
                                <input
                                    type='button'
                                    className='nh-button nh-button--primary'
                                    value={gettext('Save')}
                                    onClick={this.props.onSave}/>
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
