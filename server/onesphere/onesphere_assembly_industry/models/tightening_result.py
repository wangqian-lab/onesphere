# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import logging
from pprint import pformat
from odoo.addons.oneshare_utils.constants import ONESHARE_DEFAULT_SPC_MIN_LIMIT, ONESHARE_DEFAULT_SPC_MAX_LIMIT
from odoo.addons.onesphere_core.constants import oneshare_daq_with_track_code_rel_enable

try:
    from odoo.models import OneshareHyperModel as HModel
except ImportError:
    from odoo.models import Model as HModel

_logger = logging.getLogger(__name__)


class OperationResult(HModel):
    """
    采集拧紧数据结果表
    """
    _name = "onesphere.tightening.result"

    _description = 'Tightening Result'

    _hyper_interval = '1 month'

    _order = 'control_time DESC'

    _inherit = ["onesphere.daq.item"]

    def _compute_display_name(self):
        for result in self:
            result.display_name = result.tightening_result or 'New Tightening Result'

    tightening_process_no = fields.Char(string='Tightening Process(Pset/Job)')

    tightening_strategy = fields.Selection([('AD', 'Torque tightening'),
                                            ('AW', 'Angle tightening'),
                                            ('ADW', 'Torque/Angle tightening'),
                                            ('LN', 'Loosening'),
                                            ('AN', 'Number of Pulses tightening'),
                                            ('AT', 'Time tightening')], default='AD')  # 拧紧策略

    tightening_result = fields.Selection([
        ('none', _('No measure')),
        ('lsn', _('LSN')),
        ('ak2', _('AK2')),
        ('ok', _('OK')),
        ('nok', _('NOK'))], string="Measure Success", default='none')

    measurement_final_torque = fields.Float(string='Tightening Final Torque',
                                            digits='decimal_tightening_result_measurement')

    measurement_final_angle = fields.Float(string='Tightening Final Angle',
                                           digits='decimal_tightening_result_measurement')

    measurement_step_results = fields.Char(string='Tightening Step Results', help=u'分段拧紧结果')

    tightening_id = fields.Char(string='TighteningID', help='Tightening ID Per Tightening Controller')

    error_code = fields.Char(string='Error Code', help='Error Code')

    display_name = fields.Char(string='Display Name', compute=_compute_display_name)

    # FIXME: 拧紧曲线数据保存在数据库中, TSV格式
    curve_data = fields.Binary('Tightening Curve Data', help=u'Tightening Curve Content Data', attachment=False)
    # 目前仍将曲线保存在minio
    curve_file = fields.Char(string='Curve Files')
    tightening_unit_code = fields.Char(string='Tightening Unit Code')
    tightening_point_name = fields.Many2one('onesphere.tightening.bolt', string='Tightening Point Name')
    user_id = fields.Many2one('res.users', string='User Name')
    workcenter_code = fields.Char(string='Work Center Code')
    batch = fields.Char(string='Batch')
    barcode = fields.Char(string='Barcode')
    track_img_url = fields.Char(string='Track Image URL')
    measure_rule_result = fields.Char(string='Measure Rule Result')

    step_type = fields.Selection(
        [('tightening', 'Tightening'), ('register_byproducts', 'RegisterByProducts'), ('picture', 'Picture'),
         ('measure', 'Measure'), ('multi_measure', 'MultiMeasure')], string='Step Type')

    work_mode = fields.Selection(
        [('normal', 'Normal'), ('rework', 'Rework'), ('manual', 'Manual'),
         ('trial', 'Trial')], string='Work Mode'
    )
    user_list = fields.Char(string='User List')

    def get_tightening_result_filter_datetime(self, date_from=None, date_to=None, field=None, filter_result='ok',
                                              limit=ONESHARE_DEFAULT_SPC_MAX_LIMIT):
        if not date_to:
            date_to = fields.Datetime.now()
        if not date_from:
            date_from = fields.Datetime.today() - relativedelta(years=10)
        cr = self.env.cr
        query = '''
                SELECT r.measurement_final_torque AS torque, r.measurement_final_angle AS angle
                FROM public.onesphere_tightening_result r
                WHERE control_time between %s AND %s
                '''
        if filter_result:
            query += f'''AND tightening_result='{filter_result}' '''
        if limit:
            query += f'''limit {limit} '''
        cr.execute(query, (date_from, date_to,))
        result = cr.fetchall()
        if not result:
            raise ValidationError('查询获取结果为空,请重新定义查询参数或等待新结果数据')
        torque, angle = zip(*result)
        result = {'torque': list(torque), 'angle': list(angle)}
        _logger.debug(f"get_result_filter_datetime: {pformat(result)}")
        if not field:
            return result
        if field not in ['torque', 'angle']:
            raise ValidationError(_('Query Field Must Is torque or angle, but now is %s!!!') % field)
        return {field: result.get(field, [])}

    # FIXME: 无工单模式存储过程
    def _init_default(self):
        self.env.cr.execute("""
        CREATE OR REPLACE FUNCTION create_operation_tightening_result(
            control_date TIMESTAMP WITHOUT TIME ZONE,
            user_id BIGINT,
            pset_strategy VARCHAR,
            cur_objects VARCHAR,
            measure_result varchar,
            measure_degree NUMERIC,
            measure_torque NUMERIC,
            exception_reason VARCHAR,
            batch VARCHAR,
            r_tightening_id VARCHAR,
            gun_sn VARCHAR,
            vin_code VARCHAR,
            r_pset VARCHAR,
            measurement_step_results VARCHAR,
            tightening_unit_code VARCHAR,
            tightening_point_name VARCHAR,
            workcenter_code VARCHAR,
            barcode varchar,
            track_img_url varchar,
            measure_rule_result varchar,
            step_type varchar,
            work_mode varchar,
            user_list varchar
        ) RETURNS BIGINT AS
        $$
        DECLARE
            r_measure_result VARCHAR;
            result_id        BIGINT;
            user_name_list   VARCHAR;
            bolt_id          BIGINT;
            r_step_type      VARCHAR;
        BEGIN
        
            if length(step_type) > 0
            then
                set r_step_type = step_type;
            else
                case
                    when length(barcode) > 0 then set r_step_type = 'register_byproducts';
                    when length(track_img_url) > 0 then set r_step_type = 'picture';
                    when length(measure_rule_result) then set r_step_type = 'multi_measure';
                    else set r_step_type = 'tightening';
                    end case;
            end if;
        
            case pset_strategy
                WHEN 'LN'
                    then r_measure_result = 'lsn';
                ELSE r_measure_result = measure_result;
                end case;
        
            case when user_list = ''
                then user_name_list = null;
                else select string_agg(user_name, ',')
                     into user_name_list
                     from (select json_array_elements(user_list::json) ->> 'name' user_name) user_info;
                end case;
        
            select id into bolt_id from onesphere_tightening_bolt where name = tightening_point_name;
        
            if bolt_id is null then
                insert into onesphere_tightening_bolt (name, type)
                values (tightening_point_name, 'missing')
                ON CONFLICT (name) DO UPDATE SET name=excluded.name
                returning id into bolt_id;
            end if;
        
            INSERT INTO PUBLIC.onesphere_tightening_result (track_no,
                                                            attribute_equipment_no,
                                                            tightening_process_no,
                                                            tightening_strategy,
                                                            tightening_result,
                                                            measurement_final_torque,
                                                            measurement_final_angle,
                                                            measurement_step_results,
                                                            tightening_id,
                                                            error_code,
                                                            curve_file,
                                                            control_time,
                                                            tightening_unit_code,
                                                            tightening_point_name,
                                                            user_id,
                                                            workcenter_code,
                                                            batch,
                                                            time,
                                                            barcode,
                                                            track_img_url,
                                                            measure_rule_result,
                                                            step_type,
                                                            work_mode,
                                                            user_list)
            VALUES (vin_code,
                    gun_sn,
                    r_pset,
                    pset_strategy,
                    r_measure_result,
                    measure_torque,
                    measure_degree,
                    measurement_step_results,
                    r_tightening_id,
                    exception_reason,
                    cur_objects,
                    control_date,
                    tightening_unit_code,
                    bolt_id,
                    user_id,
                    workcenter_code,
                    batch,
                    now(),
                    barcode,
                    track_img_url,
                    measure_rule_result,
                    r_step_type,
                    work_mode,
                    user_name_list);
            result_id = lastval();
            RETURN result_id;
        
        END;
        $$ LANGUAGE plpgsql;
        """)

    def _init_with_track_code_rel(self):
        self.env.cr.execute("""
        CREATE OR REPLACE FUNCTION create_operation_tightening_result(
    control_date TIMESTAMP WITHOUT TIME ZONE,
    user_id BIGINT,
    pset_strategy VARCHAR,
    cur_objects VARCHAR,
    measure_result varchar,
    measure_degree NUMERIC,
    measure_torque NUMERIC,
    exception_reason VARCHAR,
    batch VARCHAR,
    r_tightening_id VARCHAR,
    gun_sn VARCHAR,
    vin_code VARCHAR,
    r_pset VARCHAR,
    measurement_step_results VARCHAR,
    tightening_unit_code VARCHAR,
    tightening_point_name VARCHAR,
    workcenter_code VARCHAR,
    barcode varchar,
    track_img_url varchar,
    measure_rule_result varchar,
    step_type varchar,
    work_mode varchar,
    user_list varchar
) RETURNS BIGINT AS
$$
DECLARE
    r_measure_result VARCHAR;
    result_id        BIGINT;
    user_name_list   VARCHAR;
    bolt_id          BIGINT;
    track_code_id    BIGINT;
    r_step_type      VARCHAR;
    BEGIN
    
    if length(step_type) > 0
    then
        set r_step_type = step_type;
    else
        case
            when length(barcode) > 0 then set r_step_type = 'register_byproducts';
            when length(track_img_url) > 0 then set r_step_type = 'picture';
            when length(measure_rule_result) then set r_step_type = 'multi_measure';
            else set r_step_type = 'tightening';
            end case;
    end if;

    case pset_strategy
        when 'LN'
            then r_measure_result = 'lsn';
        ELSE r_measure_result = measure_result;
        end case;

    case when user_list = ''
        then user_name_list = null;
        else select string_agg(user_name, ',')
             into user_name_list
             from (select json_array_elements(user_list::json) ->> 'name' user_name) user_info;
        end case;

    select id into bolt_id from onesphere_tightening_bolt where name = tightening_point_name;

    if bolt_id is null then
        insert into onesphere_tightening_bolt (name, type)
        values (tightening_point_name, 'missing')
        ON CONFLICT (name) DO UPDATE SET name=excluded.name
        returning id into bolt_id;
    end if;

    select id into track_code_id from public.oneshare_track_code where track_code = vin_code;

    if track_code_id is null then
        insert into public.oneshare_track_code (track_code)
        values (vin_code)
        ON CONFLICT (track_code) DO UPDATE SET track_code=excluded.track_code
        returning id into track_code_id;
    end if;

    INSERT INTO PUBLIC.onesphere_tightening_result (track_no,
                                                    attribute_equipment_no,
                                                    tightening_process_no,
                                                    tightening_strategy,
                                                    tightening_result,
                                                    measurement_final_torque,
                                                    measurement_final_angle,
                                                    measurement_step_results,
                                                    tightening_id,
                                                    error_code,
                                                    curve_file,
                                                    control_time,
                                                    tightening_unit_code,
                                                    tightening_point_name,
                                                    user_id,
                                                    workcenter_code,
                                                    batch,
                                                    time,
                                                    barcode,
                                                    track_img_url,
                                                    measure_rule_result,
                                                    step_type,
                                                    work_mode,
                                                    user_list)
    VALUES (track_code_id,
            gun_sn,
            r_pset,
            pset_strategy,
            r_measure_result,
            measure_torque,
            measure_degree,
            measurement_step_results,
            r_tightening_id,
            exception_reason,
            cur_objects,
            control_date,
            tightening_unit_code,
            bolt_id,
            user_id,
            workcenter_code,
            batch,
            now(),
            barcode,
            track_img_url,
            measure_rule_result,
            r_step_type,
            work_mode,
            user_name_list);
    result_id = lastval();
    RETURN result_id;

END;
$$ LANGUAGE plpgsql;
        """)

    def init(self):
        if not oneshare_daq_with_track_code_rel_enable():
            self._init_default()
        else:
            self._init_with_track_code_rel()
