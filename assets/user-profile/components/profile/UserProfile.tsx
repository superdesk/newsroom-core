import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {
    fetchUser,
    editUser,
    saveUser,
    setError,
} from '../../actions';
import CheckboxInput from 'assets/components/CheckboxInput';
import SelectInput from 'assets/components/SelectInput';
import TextInput from 'assets/components/TextInput';
import {getLocaleInputOptions} from 'assets/users/utils';
import {gettext} from 'assets/utils';
import {getDefaultLocale} from 'react-datepicker';

class UserProfile extends React.Component<any, any> {
    constructor(props: any) {
        super(props);
        this.save = this.save.bind(this);
    }

    isFormValid() {
        let valid = true;
        const errors: any = {};

        if (!this.props.user.first_name) {
            errors.first_name = [gettext('Please provide first name')];
            valid = false;
        }

        if (!this.props.user.last_name) {
            errors.last_name = [gettext('Please provide last name')];
            valid = false;
        }

        this.props.setError(errors);
        return valid;
    }

    save(event: any) {
        event.preventDefault();

        if (!this.isFormValid()) {
            return;
        }

        this.props.saveUser();
    }

    render() {
        const {user, onChange, errors} = this.props;
        const onCancel = () => this.props.fetchUser(this.props.user._id);
        const localeOptions = getLocaleInputOptions();
        return (
            <form className="profile-content container-fluid">
                <div className="row">
                    <div className="col-12 col-xl-8">
                        <div className="row pt-xl-4 pt-3 px-xl-4">
                            <div className="col-lg-6">
                                <TextInput
                                    name='first_name'
                                    label={gettext('First Name')}
                                    value={user.first_name}
                                    onChange={onChange}
                                    error={errors ? errors.first_name : null} />
                            </div>

                            <div className="col-lg-6">
                                <TextInput
                                    name='last_name'
                                    label={gettext('Last Name')}
                                    value={user.last_name}
                                    onChange={onChange}
                                    error={errors ? errors.last_name : null} />
                            </div>

                            <div className="col-lg-12">
                                <TextInput
                                    name='email'
                                    label={gettext('Email')}
                                    value={user.email}
                                    readOnly
                                />
                            </div>

                            <div className="col-lg-6">
                                <TextInput
                                    name='phone'
                                    label={gettext('Phone')}
                                    value={user.phone}
                                    onChange={onChange}
                                    error={errors ? errors.phone : null} />
                            </div>

                            <div className="col-lg-6">
                                <TextInput
                                    name='mobile'
                                    label={gettext('Mobile')}
                                    value={user.mobile}
                                    onChange={onChange}
                                    error={errors ? errors.mobile : null} />
                            </div>

                            <div className="col-lg-6">
                                <TextInput
                                    name='role'
                                    label={gettext('Role')}
                                    value={user.role}
                                    onChange={onChange}
                                    error={errors ? errors.role : null} />
                            </div>

                            <div className="col-lg-12">
                                <CheckboxInput
                                    name='receive_app_notifications'
                                    label={gettext('Receive inApp notifications')}
                                    value={!!user.receive_app_notifications}
                                    onChange={onChange}
                                />
                            </div>

                            <div className="col-lg-12">
                                <CheckboxInput
                                    name='receive_email'
                                    label={gettext('Receive email notifications')}
                                    value={!!user.receive_email}
                                    onChange={onChange}
                                />
                            </div>
                            {!!localeOptions.length &&
                                <div className="col-lg-6">
                                    <SelectInput
                                        name='locale'
                                        label={gettext('Language')}
                                        value={user.locale}
                                        onChange={onChange}
                                        options={localeOptions}
                                        defaultOption={getDefaultLocale()}
                                    />
                                </div>
                            }
                        </div>
                    </div>
                </div>

                <div className='profile-content__footer px-xl-4'>
                    <input
                        type='button'
                        className='btn btn-outline-secondary'
                        value={gettext('Cancel')}
                        onClick={onCancel} />

                    <input
                        type='button'
                        className='btn btn-outline-primary'
                        value={gettext('Save Changes')}
                        onClick={this.save} />
                </div>
            </form>
        );
    }
}

UserProfile.propTypes = {
    user: PropTypes.object.isRequired,
    onChange: PropTypes.func,
    errors: PropTypes.object,
    saveUser: PropTypes.func,
    setError: PropTypes.func,
    fetchUser: PropTypes.func,
};

const mapStateToProps = (state: any) => ({
    user: state.editedUser,
    errors: state.errors,
});

const mapDispatchToProps = (dispatch: any) => ({
    saveUser: () => dispatch(saveUser()),
    fetchUser: (id) => dispatch(fetchUser(id)),
    onChange: (event) => dispatch(editUser(event)),
    setError: (errors) => dispatch(setError(errors)),
});

export default connect(mapStateToProps, mapDispatchToProps)(UserProfile);
