import React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';

import TextInput from 'components/TextInput';
import CheckboxInput from 'components/CheckboxInput';
import AuditInformation from 'components/AuditInformation';
import {gettext} from 'utils';
import {sectionsPropType} from '../../features/sections/types';
import {Button} from 'components/Buttons';
import CloseButton from 'components/CloseButton';

class EditSectionFilter extends React.Component<any, any> {
    static propTypes: any;
    constructor(props: any) {
        super(props);
    }

    render() {
        return (
            <div className='list-item__preview' role={gettext('dialog')} aria-label={gettext('Edit Section Filters')}>
                <div className='list-item__preview-header'>
                    <h3>{get(this.props.sectionFilter, '_id') && this.props.sectionFilter.name || gettext('New Filter')}</h3>
                    <CloseButton onClick={this.props.onClose} />
                </div>
                <AuditInformation item={this.props.sectionFilter} />
                <form>
                    <div className="list-item__preview-form">
                        <TextInput
                            name='name'
                            label={gettext('Name')}
                            value={this.props.sectionFilter.name}
                            onChange={this.props.onChange}
                            error={this.props.errors ? this.props.errors.name : null}/>

                        <TextInput
                            name='description'
                            label={gettext('Description')}
                            value={this.props.sectionFilter.description}
                            onChange={this.props.onChange}
                            error={this.props.errors ? this.props.errors.description : null}/>

                        <div className="form-group">
                            <label htmlFor="sd_product_id">{gettext('Superdesk Product Id')}</label>
                            <input className="form-control"
                                id="sd_product_id"
                                name="sd_product_id"
                                value={this.props.sectionFilter.sd_product_id || ''}
                                onChange={this.props.onChange}
                            />
                            {this.props.sectionFilter.sd_product_id &&
                            <a href={`/${this.props.sectionFilter.filter_type || 'wire'}?q=products.code:${this.props.sectionFilter.sd_product_id}`} target="_blank"
                                className='nh-button nh-button--tertiary float-end mt-2'>{gettext('Test Superdesk Product id')}
                            </a>}
                        </div>

                        <div className="form-group">
                            <label htmlFor="query">{gettext('Query')}</label>
                            <textarea className="form-control"
                                id="query"
                                name="query"
                                value={this.props.sectionFilter.query || ''}
                                onChange={this.props.onChange}
                            />
                            {this.props.sectionFilter.query &&
                            <a href={`/${this.props.sectionFilter.search_type || this.props.sectionFilter.filter_type || 'wire'}?q=${this.props.sectionFilter.query}`} target="_blank"
                                className='nh-button nh-button--tertiary float-end mt-3'>{gettext('Test query')}
                            </a>}
                        </div>

                        <CheckboxInput
                            name='is_enabled'
                            label={gettext('Enabled')}
                            value={this.props.sectionFilter.is_enabled}
                            onChange={this.props.onChange}/>

                    </div>
                    <div className='list-item__preview-footer'>
                        <Button
                            value={gettext('Delete')}
                            variant='secondary'
                            onClick={this.props.onDelete}
                        />

                        <Button
                            value={gettext('Save')}
                            variant='primary'
                            onClick={this.props.onSave}
                        />
                    </div>
                </form>
            </div>
        );
    }
}

EditSectionFilter.propTypes = {
    sectionFilter: PropTypes.object.isRequired,
    onChange: PropTypes.func,
    errors: PropTypes.object,
    onSave: PropTypes.func.isRequired,
    onClose: PropTypes.func.isRequired,
    onDelete: PropTypes.func.isRequired,
    sections: sectionsPropType,
};

export default EditSectionFilter;
