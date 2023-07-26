import React from 'react';
import PropTypes from 'prop-types';
import TextInput from 'components/TextInput';
import CheckboxInput from 'components/CheckboxInput';
import EditPanel from 'components/EditPanel';
import FileInput from 'components/FileInput';
import {get} from 'lodash';

import {gettext} from 'utils';
import {sectionsPropType} from 'features/sections/types';
import {MAX_TILE_IMAGES} from '../actions';
import AuditInformation from 'components/AuditInformation';


class EditNavigation extends React.Component<any, any> {
    static propTypes: any;
    tabs: any;
    sectionIds: any;
    constructor(props: any) {
        super(props);
        this.handleTabClick = this.handleTabClick.bind(this);
        this.state = {activeTab: 'navigation-details'};

        this.tabs = [
            {label: gettext('Global Topic'), name: 'navigation-details'},
            {label: gettext('Products'), name: 'products'}
        ];

        this.sectionIds = this.props.sections.map((section: any) => section._id);
    }

    handleTabClick(event: any) {
        this.setState({activeTab: event.target.title});
        if(event.target.title === 'products' && this.props.navigation._id) {
            this.props.fetchProducts();
        }
    }

    render() {
        const tile_images = get(this.props, 'navigation.tile_images') || [];
        const getActiveSection = () => this.props.sections.filter(
            (s: any) => s._id === get(this.props.navigation, 'product_type')
        );

        return (
            <div className='list-item__preview' role={gettext('dialog')} aria-label={gettext('Edit Navigation')}>
                <div className='list-item__preview-header'>
                    <h3>{this.props.navigation.name}</h3>
                    <button
                        id='hide-sidebar'
                        type='button'
                        className='icon-button'
                        data-bs-dismiss='modal'
                        aria-label={gettext('Close')}
                        onClick={this.props.onClose}>
                        <i className="icon--close-thin icon--gray-dark" aria-hidden='true'></i>
                    </button>
                </div>
                <AuditInformation item={this.props.navigation} />

                <ul className='nav nav-tabs'>
                    {this.tabs.map((tab: any) => (
                        <li key={tab.name} className='nav-item'>
                            <a
                                title={tab.name}
                                className={`nav-link ${this.state.activeTab === tab.name && 'active'}`}
                                href='#'
                                onClick={this.handleTabClick}
                            >
                                {tab.label}
                            </a>
                        </li>
                    ))}
                </ul>

                <div className='tab-content'>
                    {this.state.activeTab === 'navigation-details' &&
                        <div className='tab-pane active' id='navigation-details'>
                            <form>
                                <div className="list-item__preview-form">
                                    <TextInput
                                        name='name'
                                        label={gettext('Name')}
                                        value={this.props.navigation.name}
                                        onChange={this.props.onChange}
                                        error={this.props.errors ? this.props.errors.name : null}/>

                                    <TextInput
                                        name='description'
                                        label={gettext('Description')}
                                        value={this.props.navigation.description}
                                        onChange={this.props.onChange}
                                        error={this.props.errors ? this.props.errors.description : null}/>

                                    <CheckboxInput
                                        name='is_enabled'
                                        label={gettext('Enabled')}
                                        value={this.props.navigation.is_enabled}
                                        onChange={this.props.onChange}/>

                                    {this.sectionIds.includes('aapX') && (
                                        <div className="card mt-3 d-block">
                                            <div className="card-header">{'Tile Images (Marketplace)'}</div>
                                            <div className="card-body">
                                                {[...Array(MAX_TILE_IMAGES)].map((_: any, index: any) => (
                                                    <FileInput key={index}
                                                        name={`tile_images_file_${index}`}
                                                        label={get(tile_images, `[${index}.file]`) ||
                                                        `${gettext('Upload Image')} ${index + 1}`}
                                                        onChange={this.props.onChange}
                                                        error={this.props.errors ? this.props.errors.tile_images : null}/>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                                <div className='list-item__preview-footer'>
                                    <input
                                        type='button'
                                        className='nh-button nh-button--secondary'
                                        value={gettext('Delete')}
                                        onClick={this.props.onDelete}/>
                                    <input
                                        type='button'
                                        className='nh-button nh-button--primary'
                                        value={gettext('Save')}
                                        onClick={this.props.onSave}/>
                                </div>
                            </form>
                        </div>
                    }
                    {this.state.activeTab === 'products' &&
                        <EditPanel
                            parent={{_id: this.props.navigation._id, products: this.props.navigation.products}}
                            items={this.props.products}
                            field="products"
                            onSave={this.props.onSave}
                            groups={getActiveSection()}
                            groupField={'product_type'}
                            groupDefaultValue={'wire'}
                            onChange={this.props.onChange}
                        />
                    }
                </div>
            </div>
        );
    }
}

EditNavigation.propTypes = {
    navigation: PropTypes.object.isRequired,
    onChange: PropTypes.func,
    errors: PropTypes.object,
    products: PropTypes.arrayOf(PropTypes.object),
    onSave: PropTypes.func.isRequired,
    onClose: PropTypes.func.isRequired,
    onDelete: PropTypes.func.isRequired,
    fetchProducts: PropTypes.func.isRequired,
    sections: sectionsPropType,
};

export default EditNavigation;
