import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';
import {connect} from 'react-redux';
import {get, sortBy} from 'lodash';

import {save} from '../actions';

import TextInput from 'components/TextInput';
import CheckboxInput from 'components/CheckboxInput';
import AuditInformation from 'components/AuditInformation';

function isInput(field: any) {
    return ['text', 'number', 'boolean'].includes(field.type);
}

class GeneralSettingsApp extends React.Component<any, any> {
    constructor(props: any) {
        super(props);
        this.state = {
            values: {},
            _updated: get(this.props, 'config._updated'),
        };
        Object.keys(props.config).forEach((key) => {
            const config = props.config[key] || {};

            this.state.values[key] = (() => {
                switch (config.type) {
                case 'text':
                    return config.value || config.default || '';
                case 'number':
                    return config.value || config.default || 0;
                case 'boolean':
                    return config.value != null ? config.value : config.default || false;
                }
            })();
        });

        this.onSubmit = this.onSubmit.bind(this);
    }

    componentWillReceiveProps(nextProps: any) {
        if (nextProps.updatedTime !== this.props.updatedTime) {
            this.setState({
                _updated: nextProps.updatedTime
            });
        }
    }

    onChange(key: any, val: any) {
        const values = {...this.state.values, [key]: val};
        this.setState({values});
    }

    onBooleanChange(key: any) {
        const values = {...this.state.values, [key]: !this.state.values[key]};
        this.setState({values});
    }

    onSubmit(event: any) {
        event.preventDefault();
        this.props.save(this.state.values);
    }

    render() {
        const {config} = this.props;
        const fields = sortBy(Object.keys(config), (_id) => config[_id].weight).map((_id) => {
            const field = config[_id];
            if (isInput(field)) {
                return field.type === 'boolean' ? (
                    <div className="form-group">
                        <CheckboxInput
                            key={_id}
                            name={_id}
                            label={gettext(field.label)}
                            onChange={this.onBooleanChange.bind(this, _id)}
                            value={this.state.values[_id]}
                        />
                    </div>
                ) : (
                    <TextInput
                        key={_id}
                        type={field.type}
                        name={_id}
                        label={gettext(field.label)}
                        value={this.state.values[_id]}
                        placeholder={field.default ? field.default.toString() : ''}
                        onChange={(event: any) => this.onChange(_id, event.target.value)}
                        description={gettext(field.description)}
                        min={field.min}
                    />
                );
            }
            return null;
        });
        const audit = {
            '_updated': this.props.updatedTime,
            'version_creator': this.props.versionCreator
        };

        return (
            <div className="flex-row">
                <div className="flex-col flex-column">
                    <section className="content-main">
                        <div className="list-items-container">
                            <AuditInformation item={audit} noPadding/>
                            <form onSubmit={this.onSubmit}>
                                {fields}

                                <button type="submit" className="btn btn-primary">{gettext('Save')}</button>
                            </form>
                        </div>
                    </section>
                </div>
            </div>
        );
    }
}

GeneralSettingsApp.propTypes = {
    config: PropTypes.object.isRequired,
    save: PropTypes.func.isRequired,
    updatedTime: PropTypes.string,
    versionCreator: PropTypes.string,
};

const mapStateToProps = (state: any) => ({
    config: state.config,
    updatedTime: state._updated,
    versionCreator: state.version_creator,
});

const mapDispatchToProps = {
    save,
};

export default connect(mapStateToProps, mapDispatchToProps)(GeneralSettingsApp);
